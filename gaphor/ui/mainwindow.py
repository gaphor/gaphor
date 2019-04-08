"""
The main application window.
"""

import logging
import os.path
from zope import component
from zope.interface import implementer

import pkg_resources
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import Gtk

from gaphor import UML
from gaphor.UML.event import ModelFactoryEvent
from gaphor.core import (
    _,
    inject,
    action,
    toggle_action,
    build_action_group,
    transactional,
)
from gaphor.interfaces import IService, IActionProvider
from gaphor.UML.interfaces import IAttributeChangeEvent
from gaphor.services.filemanager import FileManagerStateChanged
from gaphor.services.undomanager import UndoManagerStateChanged
from gaphor.ui.accelmap import load_accel_map, save_accel_map
from gaphor.ui.diagrampage import DiagramPage
from gaphor.ui.event import DiagramPageChange, DiagramShow
from gaphor.ui.interfaces import IUIComponent
from gaphor.ui.layout import deserialize
from gaphor.ui.namespace import Namespace
from gaphor.ui.toolbox import Toolbox

log = logging.getLogger(__name__)

ICONS = (
    "gaphor-24x24.png",
    "gaphor-48x48.png",
    "gaphor-96x96.png",
    "gaphor-256x256.png",
)


@implementer(IService, IActionProvider)
class MainWindow(object):
    """
    The main window for the application.
    It contains a Namespace-based tree view and a menu and a statusbar.
    """

    component_registry = inject("component_registry")
    properties = inject("properties")
    element_factory = inject("element_factory")
    action_manager = inject("action_manager")
    file_manager = inject("file_manager")
    ui_manager = inject("ui_manager")

    title = "Gaphor"
    size = property(lambda s: s.properties.get("ui.window-size", (760, 580)))
    menubar_path = "/mainwindow"
    toolbar_path = "/mainwindow-toolbar"
    resizable = True

    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="file">
            <placeholder name="primary" />
            <separator />
            <menu action="file-export" />
            <menu action="file-import" />
            <separator />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
            <separator />
            <menuitem action="file-quit" />
          </menu>
          <menu action="edit">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
          <menu action="diagram">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
          <menu action="tools">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
          <menu action="help">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
        </menubar>
        <toolbar name='mainwindow-toolbar'>
            <placeholder name="left" />
            <separator expand="true" />
            <placeholder name="right" />
        </toolbar>
      </ui>
    """

    def __init__(self):
        self.app = None
        self.window = None
        self.model_changed = False
        self.layout = None

    def init(self, app=None):
        self.app = app
        self.init_stock_icons()
        self.init_action_group()
        self.init_ui_components()

    def init_stock_icons(self):
        # Load stock items
        import gaphor.ui.stock

        gaphor.ui.stock.load_stock_icons()

    def init_ui_components(self):
        component_registry = self.component_registry
        for ep in pkg_resources.iter_entry_points("gaphor.uicomponents"):
            log.debug("found entry point uicomponent.%s" % ep.name)
            cls = ep.load()
            if not IUIComponent.implementedBy(cls):
                raise NameError(
                    "Entry point %s doesn" "t provide IUIComponent" % ep.name
                )
            uicomp = cls()
            uicomp.ui_name = ep.name
            component_registry.register_utility(uicomp, IUIComponent, ep.name)
            if IActionProvider.providedBy(uicomp):
                self.action_manager.register_action_provider(uicomp)

    def shutdown(self):
        log.info("Shutting down")
        if self.window:
            self.window.destroy()
            self.window = None
        save_accel_map()

        cr = self.component_registry
        cr.unregister_handler(self._on_file_manager_state_changed)
        cr.unregister_handler(self._on_undo_manager_state_changed)
        cr.unregister_handler(self._new_model_content)

    def init_action_group(self):
        self.action_group = build_action_group(self)
        for name, label in (
            ("file", "_File"),
            ("file-export", "_Export"),
            ("file-import", "_Import"),
            ("edit", "_Edit"),
            ("diagram", "_Diagram"),
            ("tools", "_Tools"),
            ("help", "_Help"),
        ):
            a = Gtk.Action.new(name, label, None, None)
            a.set_property("hide-if-empty", False)
            self.action_group.add_action(a)

        self.action_manager.register_action_provider(self)

    def get_filename(self):
        """
        Return the file name of the currently opened model.
        """
        return self.file_manager.filename

    def ask_to_close(self):
        """
        Ask user to close window if the model has changed.
        The user is asked to either discard the changes, keep the
        application running or save the model and quit afterwards.
        """
        if self.model_changed:
            dialog = Gtk.MessageDialog(
                self.window,
                Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.WARNING,
                Gtk.ButtonsType.NONE,
                _("Save changed to your model before closing?"),
            )
            dialog.format_secondary_text(
                _("If you close without saving, your changes will be discarded.")
            )
            dialog.add_buttons(
                "Close _without saving",
                Gtk.ResponseType.REJECT,
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE,
                Gtk.ResponseType.YES,
            )
            dialog.set_default_response(Gtk.ResponseType.YES)
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
                # On filedialog.cancel, the application should not close.
                return self.file_manager.action_save()
            return response == Gtk.ResponseType.REJECT
        return True

    def get_ui_component(self, name):
        return self.component_registry.get_utility(IUIComponent, name)

    def open(self, gtk_app=None):
        """Open the main window.
        """
        load_accel_map()

        self.window = (
            Gtk.ApplicationWindow.new(gtk_app)
            if gtk_app
            else Gtk.Window.new(type=Gtk.WindowType.TOPLEVEL)
        )
        self.window.set_title(self.title)
        self.window.set_default_size(*self.size)

        # set default icons of gaphor windows
        icon_dir = os.path.abspath(
            pkg_resources.resource_filename("gaphor.ui", "pixmaps")
        )
        icons = (
            GdkPixbuf.Pixbuf.new_from_file(os.path.join(icon_dir, f)) for f in ICONS
        )
        self.window.set_icon_list(list(icons))

        self.window.add_accel_group(self.ui_manager.get_accel_group())

        # Create a full featured window.
        vbox = Gtk.VBox()
        self.window.add(vbox)
        vbox.show()

        menubar = self.ui_manager.get_widget(self.menubar_path)
        if menubar:
            vbox.pack_start(menubar, False, True, 0)

        toolbar = self.ui_manager.get_widget(self.toolbar_path)
        if toolbar:
            vbox.pack_start(toolbar, False, True, 0)

        def _factory(name):
            comp = self.get_ui_component(name)
            log.debug("open component %s" % str(comp))
            return comp.open()

        layout_file = pkg_resources.resource_filename("gaphor.ui", "layout.xml")
        self.layout = []  # Gtk.Notebook()

        with open(layout_file) as f:
            deserialize(self.layout, vbox, f.read(), _factory)

        vbox.show()
        # TODO: add statusbar

        self.window.present()

        self.window.connect("delete-event", self._on_window_delete)

        # We want to store the window size, so it can be reloaded on startup
        self.window.set_resizable(True)
        self.window.connect("size-allocate", self._on_window_size_allocate)

        cr = self.component_registry
        cr.register_handler(self._on_file_manager_state_changed)
        cr.register_handler(self._on_undo_manager_state_changed)
        cr.register_handler(self._new_model_content)

    def open_welcome_page(self):
        """
        Create a new tab with a textual welcome page, a sort of 101 for
        Gaphor.
        """
        pass

    def set_title(self):
        """
        Sets the window title.
        """
        filename = self.file_manager.filename
        if self.window:
            if filename:
                title = "%s - %s" % (self.title, filename)
            else:
                title = self.title
            if self.model_changed:
                title += " *"
            self.window.set_title(title)

    # Signal callbacks:

    @component.adapter(ModelFactoryEvent)
    def _new_model_content(self, event):
        """
        Open the toplevel element and load toplevel diagrams.
        """
        # TODO: Make handlers for ModelFactoryEvent from within the GUI obj
        for diagram in self.element_factory.select(
            lambda e: e.isKindOf(UML.Diagram)
            and not (e.namespace and e.namespace.namespace)
        ):
            self.component_registry.handle(DiagramShow(diagram))

    @component.adapter(FileManagerStateChanged)
    def _on_file_manager_state_changed(self, event):
        # We're only interested in file operations
        if event.service is self.file_manager:
            self.model_changed = False
            self.set_title()

    @component.adapter(UndoManagerStateChanged)
    def _on_undo_manager_state_changed(self, event):
        """
        """
        undo_manager = event.service
        if not self.model_changed and undo_manager.can_undo():
            self.model_changed = True
            self.set_title()

    def _on_window_delete(self, window=None, event=None):
        return not self.ask_to_close()

    def _on_window_size_allocate(self, window, allocation):
        """
        Store the window size in a property.
        """
        self.properties.set("ui.window-size", (allocation.width, allocation.height))

    # Actions:

    @action(name="file-quit", stock_id="gtk-quit")
    def quit(self):
        # TODO: check for changes (e.g. undo manager), fault-save
        close = self.ask_to_close()
        if close and self.app:
            self.app.quit()

    # TODO: Does not belong here
    def create_item(self, ui_component):
        """
        Create an item for a ui component. This method can be called from UIComponents.
        """
        window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        window.set_transient_for(self.window)
        window.set_title(ui_component.title)
        window.add(ui_component.open())
        window.show()
        window.ui_component = ui_component


Gtk.AccelMap.add_filter("gaphor")


@implementer(IUIComponent, IActionProvider)
class Diagrams(object):

    title = _("Diagrams")
    placement = ("left", "diagrams")

    component_registry = inject("component_registry")
    properties = inject("properties")
    ui_manager = inject("ui_manager")

    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="diagram">
            <separator/>
            <menuitem action="diagram-drawing-style" />
            <separator/>
          </menu>
        </menubar>
      </ui>
    """

    def __init__(self):
        self._notebook = None
        self.action_group = build_action_group(self)
        self.action_group.get_action("diagram-drawing-style").set_active(
            self.properties("diagram.sloppiness", 0) != 0
        )
        self._page_ui_settings = None

    def open(self):
        """Open the diagrams component.

        Returns:
            The Gtk.Notebook.
        """

        self._notebook = Gtk.Notebook()
        self._notebook.show()
        self._notebook.connect("switch-page", self._on_switch_page)
        self.component_registry.register_handler(self._on_show_diagram)
        self.component_registry.register_handler(self._on_name_change)
        return self._notebook

    def close(self):
        """Close the diagrams component."""

        self.component_registry.unregister_handler(self._on_name_change)
        self.component_registry.unregister_handler(self._on_show_diagram)
        self._notebook.destroy()
        self._notebook = None

    def get_current_diagram(self):
        """Returns the current page of the notebook.

        Returns (DiagramPage): The current diagram page.
        """

        page_num = self._notebook.get_current_page()
        child_widget = self._notebook.get_nth_page(page_num)
        if child_widget is not None:
            return child_widget.diagram_page.get_diagram()
        else:
            return None

    def get_current_view(self):
        """Returns the current view of the diagram page.

        Returns (GtkView): The current view.
        """
        if not self._notebook:
            return
        page_num = self._notebook.get_current_page()
        child_widget = self._notebook.get_nth_page(page_num)
        return child_widget.diagram_page.get_view()

    def cb_close_tab(self, button, widget):
        """Callback to close the tab and remove the notebook page.

        Args:
            button (Gtk.Button): The button the callback is from.
            widget (Gtk.Widget): The child widget of the tab.
        """

        page_num = self._notebook.page_num(widget)
        # TODO why does Gtk.Notebook give a GTK-CRITICAL if you remove a page
        #   with set_show_tabs(True)?
        self._clear_ui_settings()
        self._notebook.remove_page(page_num)
        widget.diagram_page.close()
        widget.destroy()

    def create_tab(self, title, widget):
        """Creates a new Notebook tab with a label and close button.

        Args:
            title (str): The title of the tab, the diagram name.
            widget (Gtk.Widget): The child widget of the tab.
        """

        page_num = self._notebook.append_page(
            child=widget, tab_label=self.tab_label(title, widget)
        )
        self._notebook.set_current_page(page_num)
        self._notebook.set_tab_reorderable(widget, True)

        self.component_registry.handle(DiagramPageChange(widget))
        self._notebook.set_show_tabs(True)

    def tab_label(self, title, widget):
        tab_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        label = Gtk.Label(label=title)
        tab_box.pack_start(label)

        close_image = Gtk.Image.new_from_icon_name(
            icon_name="window-close", size=Gtk.IconSize.MENU
        )
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_focus_on_click(False)
        button.add(close_image)
        button.connect("clicked", self.cb_close_tab, widget)
        tab_box.pack_start(child=button, expand=False, fill=False, padding=0)
        tab_box.show_all()
        return tab_box

    def get_widgets_on_pages(self):
        """Gets the widget on each open page Notebook page.

        The page is the page number in the Notebook (0 indexed) and the widget
        is the child widget on each page.

        Returns:
            List of tuples (page, widget) of the currently open Notebook pages.
        """

        widgets_on_pages = []
        if not self._notebook:
            return widgets_on_pages

        num_pages = self._notebook.get_n_pages()
        for page in range(0, num_pages):
            widget = self._notebook.get_nth_page(page)
            widgets_on_pages.append((page, widget))
        return widgets_on_pages

    def _on_switch_page(self, notebook, page, page_num):
        self._clear_ui_settings()
        self._add_ui_settings(page_num)
        self.component_registry.handle(DiagramPageChange(page))

    def _add_ui_settings(self, page_num):
        ui_manager = self.ui_manager
        child_widget = self._notebook.get_nth_page(page_num)
        action_group = child_widget.diagram_page.action_group
        menu_xml = child_widget.diagram_page.menu_xml
        ui_manager.insert_action_group(action_group)
        ui_id = ui_manager.add_ui_from_string(menu_xml)
        self._page_ui_settings = (action_group, ui_id)

    def _clear_ui_settings(self):
        ui_manager = self.ui_manager
        if self._page_ui_settings:
            action_group, ui_id = self._page_ui_settings
            self.ui_manager.remove_action_group(action_group)
            self.ui_manager.remove_ui(ui_id)
            self._page_ui_settings = None

    @component.adapter(DiagramShow)
    def _on_show_diagram(self, event):
        """Show a Diagram element in the Notebook.

        If a diagram is already open on a Notebook page, show that one,
        otherwise create a new Notebook page.

        Args:
            event: The service event that is calling the method.
        """

        diagram = event.diagram

        # Try to find an existing diagram page and give it focus
        for page, widget in self.get_widgets_on_pages():
            if widget.diagram_page.get_diagram() is diagram:
                self._notebook.set_current_page(page)
                return widget.diagram_page

        # No existing diagram page found, creating one
        page = DiagramPage(diagram)
        widget = page.construct()
        try:
            widget.set_css_name("diagram-tab")
        except AttributeError:
            pass  # Gtk.Widget.set_css_name() is added in 3.20
        widget.set_name("diagram-tab")
        widget.diagram_page = page
        page.set_drawing_style(self.properties("diagram.sloppiness", 0))

        self.create_tab(diagram.name, widget)
        return page

    @component.adapter(IAttributeChangeEvent)
    def _on_name_change(self, event):
        if event.property is UML.Diagram.name:
            for page in range(0, self._notebook.get_n_pages()):
                widget = self._notebook.get_nth_page(page)
                if event.element is widget.diagram_page.diagram:
                    print("Name change", event.__dict__)
                    self._notebook.set_tab_label(
                        widget, self.tab_label(event.new_value, widget)
                    )

    @toggle_action(name="diagram-drawing-style", label="Hand drawn style", active=False)
    def hand_drawn_style(self, active):
        """Toggle between straight diagrams and "hand drawn" diagram style."""

        if active:
            sloppiness = 0.5
        else:
            sloppiness = 0.0
        for page, widget in self.get_widgets_on_pages():
            widget.diagram_page.set_drawing_style(sloppiness)
        self.properties.set("diagram.sloppiness", sloppiness)
