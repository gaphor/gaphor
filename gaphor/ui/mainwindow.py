"""
The main application window.
"""

import logging
import os.path
from builtins import object
from builtins import str
from zope import component

from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GdkPixbuf
import pkg_resources
from zope.interface import implementer

from gaphor import UML
from gaphor.UML.event import ModelFactoryEvent
from gaphor.core import (
    _,
    inject,
    action,
    toggle_action,
    open_action,
    build_action_group,
    transactional,
)
from gaphor.interfaces import IService, IActionProvider
from gaphor.services.filemanager import FileManagerStateChanged
from gaphor.services.undomanager import UndoManagerStateChanged
from gaphor.ui.accelmap import load_accel_map, save_accel_map
from gaphor.ui.diagrampage import DiagramPage
from gaphor.ui.diagramtoolbox import TOOLBOX_ACTIONS
from gaphor.ui.event import DiagramPageChange, Diagram
from gaphor.ui.interfaces import IDiagramPageChange
from gaphor.ui.interfaces import IUIComponent
from gaphor.ui.layout import deserialize
from gaphor.ui.namespace import NamespaceModel, NamespaceView
from gaphor.ui.toolbox import Toolbox as _Toolbox

log = logging.getLogger(__name__)

ICONS = (
    "gaphor-24x24.png",
    "gaphor-48x48.png",
    "gaphor-96x96.png",
    "gaphor-256x256.png",
)

STATIC_MENU_XML = """
  <ui>
    <menubar name="mainwindow">
      <menu action="%s">
        <menuitem action="%s" />
      </menu>
    </menubar>
  </ui>
"""


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
        self.window = None
        self.model_changed = False
        self.layout = None

    def init(self, app=None):
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
        self._tab_ui_settings = None

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

    def get_widgets(self, name):
        return []

    def open(self):

        load_accel_map()

        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
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
            comp = self.component_registry.get_utility(IUIComponent, name)
            log.debug("open component %s" % str(comp))
            return comp.open()

        filename = pkg_resources.resource_filename("gaphor.ui", "layout.xml")
        self.layout = []  # Gtk.Notebook()

        with open(filename) as f:
            deserialize(self.layout, vbox, f.read(), _factory)

        vbox.show()
        # TODO: add statusbar

        self.window.show()

        self.window.connect("delete-event", self._on_window_delete)

        # We want to store the window size, so it can be reloaded on startup
        self.window.set_resizable(True)
        self.window.connect("size-allocate", self._on_window_size_allocate)
        self.window.connect("destroy", self._on_window_destroy)

        cr = self.component_registry
        cr.register_handler(self._on_file_manager_state_changed)
        cr.register_handler(self._on_undo_manager_state_changed)
        cr.register_handler(self._new_model_content)
        # TODO: register on ElementCreate/Delete event

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
            self.component_registry.handle(Diagram(diagram))

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

    def _on_window_destroy(self, window):
        """
        Window is destroyed... Quit the application.
        """
        self.window = None
        if GLib.main_depth() > 0:
            Gtk.main_quit()
        cr = self.component_registry
        cr.unregister_handler(self._on_undo_manager_state_changed)
        cr.unregister_handler(self._on_file_manager_state_changed)
        cr.unregister_handler(self._new_model_content)

    def _on_window_delete(self, window=None, event=None):
        return not self.ask_to_close()

    def _clear_ui_settings(self):
        try:
            ui_manager = self.ui_manager
        except component.ComponentLookupError as e:
            log.warning("No UI manager service found")
        else:
            if self._tab_ui_settings:
                action_group, ui_id = self._tab_ui_settings
                self.ui_manager.remove_action_group(action_group)
                self.ui_manager.remove_ui(ui_id)
                self._tab_ui_settings = None

    def _on_window_size_allocate(self, window, allocation):
        """
        Store the window size in a property.
        """
        self.properties.set("ui.window-size", (allocation.width, allocation.height))

    # Actions:

    @action(name="file-quit", stock_id="gtk-quit")
    def quit(self):
        # TODO: check for changes (e.g. undo manager), fault-save
        self.ask_to_close() and Gtk.main_quit()
        self.shutdown()

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
class Namespace(object):

    title = _("Namespace")
    placement = ("left", "diagrams")

    component_registry = inject("component_registry")
    element_factory = inject("element_factory")
    ui_manager = inject("ui_manager")
    action_manager = inject("action_manager")

    _menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="diagram">
            <separator />
            <menuitem action="tree-view-create-diagram" />
            <menuitem action="tree-view-create-package" />
            <separator />
            <menuitem action="tree-view-delete-diagram" />
            <menuitem action="tree-view-delete-package" />
            <separator />
          </menu>
        </menubar>
        <popup action="namespace-popup">
          <menuitem action="tree-view-open" />
          <menuitem action="tree-view-rename" />
          <separator />
          <menuitem action="tree-view-create-diagram" />
          <menuitem action="tree-view-create-package" />
          <separator />
          <menuitem action="tree-view-delete-diagram" />
          <menuitem action="tree-view-delete-package" />
          <separator />
          <menuitem action="tree-view-refresh" />
        </popup>
      </ui>
    """

    def __init__(self):
        self._namespace = None
        self._ui_id = None
        self.action_group = build_action_group(self)

    def open(self):
        widget = self.construct()
        self.component_registry.register_handler(self.expand_root_nodes)
        return widget

    def close(self):
        if self._namespace:
            self._namespace.destroy()
            self._namespace = None

            # TODO: How to ensure stuff is removed properly from services?
            # self.ui_manager.remove_ui(self._ui_id)
        self.component_registry.unregister_handler(self.expand_root_nodes)

    def construct(self):
        self._ui_id = self.ui_manager.add_ui_from_string(self._menu_xml)

        model = NamespaceModel(self.element_factory)
        view = NamespaceView(model, self.element_factory)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
        scrolled_window.set_placement(Gtk.CornerType.TOP_RIGHT)
        scrolled_window.add(view)
        scrolled_window.show()
        view.show()

        view.connect_after("event-after", self._on_view_event)
        view.connect("row-activated", self._on_view_row_activated)
        view.connect_after("cursor-changed", self._on_view_cursor_changed)
        view.connect("destroy", self._on_view_destroyed)
        self._namespace = view
        self.expand_root_nodes()

        return scrolled_window

    @component.adapter(ModelFactoryEvent)
    def expand_root_nodes(self, event=None):
        """
        """
        # Expand all root elements:
        self._namespace.expand_root_nodes()
        self._on_view_cursor_changed(self._namespace)

    def _on_view_event(self, view, event):
        """
        Show a popup menu if button3 was pressed on the TreeView.
        """
        # handle mouse button 3:
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            menu = self.ui_manager.get_widget("/namespace-popup")
            menu.popup(None, None, None, event.button, event.time)

    def _on_view_row_activated(self, view, path, column):
        """
        Double click on an element in the tree view.
        """
        self.action_manager.execute("tree-view-open")

    def _on_view_cursor_changed(self, view):
        """
        Another row is selected, execute a dummy action.
        """
        element = view.get_selected_element()
        self.action_group.get_action(
            "tree-view-create-diagram"
        ).props.sensitive = isinstance(element, UML.Package)
        self.action_group.get_action(
            "tree-view-create-package"
        ).props.sensitive = isinstance(element, UML.Package)

        self.action_group.get_action(
            "tree-view-delete-diagram"
        ).props.visible = isinstance(element, UML.Diagram)
        self.action_group.get_action("tree-view-delete-package").props.visible = (
            isinstance(element, UML.Package) and not element.presentation
        )

        self.action_group.get_action("tree-view-open").props.sensitive = isinstance(
            element, UML.Diagram
        )

    def _on_view_destroyed(self, widget):
        self.close()

    def select_element(self, element):
        """
        Select an element from the Namespace view.
        The element is selected. After this an action may be executed,
        such as OpenModelElement, which will try to open the element (if it's
        a Diagram).
        """
        path = Gtk.TreePath.new_from_indices(
            self._namespace.get_model().path_from_element(element)
        )
        # Expand the first row:
        if len(path.get_indices()) > 1:
            self._namespace.expand_row(path=path, open_all=False)
        selection = self._namespace.get_selection()
        selection.select_path(path)
        self._on_view_cursor_changed(self._namespace)

    @action(name="tree-view-open", label="_Open")
    def tree_view_open_selected(self):
        element = self._namespace.get_selected_element()
        # TODO: Candidate for adapter?
        if isinstance(element, UML.Diagram):
            self.component_registry.handle(Diagram(element))

        else:
            log.debug("No action defined for element %s" % type(element).__name__)

    @action(name="tree-view-rename", label=_("Rename"), accel="F2")
    def tree_view_rename_selected(self):
        view = self._namespace
        element = view.get_selected_element()
        path = view.get_model().path_from_element(element)
        column = view.get_column(0)
        cell = column.get_cells()[1]
        cell.set_property("editable", 1)
        cell.set_property("text", element.name)
        view.set_cursor(path, column, True)
        cell.set_property("editable", 0)

    @action(
        name="tree-view-create-diagram",
        label=_("_New diagram"),
        stock_id="gaphor-diagram",
    )
    @transactional
    def tree_view_create_diagram(self):
        element = self._namespace.get_selected_element()
        diagram = self.element_factory.create(UML.Diagram)
        diagram.package = element

        if element:
            diagram.name = "%s diagram" % element.name
        else:
            diagram.name = "New diagram"

        self.select_element(diagram)
        self.component_registry.handle(Diagram(diagram))
        self.tree_view_rename_selected()

    @action(
        name="tree-view-delete-diagram",
        label=_("_Delete diagram"),
        stock_id="gtk-delete",
    )
    @transactional
    def tree_view_delete_diagram(self):
        diagram = self._namespace.get_selected_element()
        m = Gtk.MessageDialog(
            None,
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO,
            "Do you really want to delete diagram %s?\n\n"
            "This will possibly delete diagram items\n"
            "that are not shown in other diagrams." % (diagram.name or "<None>"),
        )
        if m.run() == Gtk.ResponseType.YES:
            for i in reversed(diagram.canvas.get_all_items()):
                s = i.subject
                if s and len(s.presentation) == 1:
                    s.unlink()
                i.unlink
            diagram.unlink()
        m.destroy()

    @action(
        name="tree-view-create-package",
        label=_("New _package"),
        stock_id="gaphor-package",
    )
    @transactional
    def tree_view_create_package(self):
        element = self._namespace.get_selected_element()
        package = self.element_factory.create(UML.Package)
        package.package = element

        if element:
            package.name = "%s package" % element.name
        else:
            package.name = "New model"

        self.select_element(package)
        self.tree_view_rename_selected()

    @action(
        name="tree-view-delete-package",
        label=_("Delete pac_kage"),
        stock_id="gtk-delete",
    )
    @transactional
    def tree_view_delete_package(self):
        package = self._namespace.get_selected_element()
        assert isinstance(package, UML.Package)
        package.unlink()

    @action(name="tree-view-refresh", label=_("_Refresh"))
    def tree_view_refresh(self):
        self._namespace.get_model().refresh()


@implementer(IUIComponent, IActionProvider)
class Toolbox(object):

    title = _("Toolbox")
    placement = ("left", "diagrams")

    component_registry = inject("component_registry")
    main_window = inject("main_window")
    properties = inject("properties")

    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="diagram">
            <separator/>
            <menuitem action="reset-tool-after-create" />
            <separator/>
          </menu>
        </menubar>
      </ui>
    """

    def __init__(self):
        self._toolbox = None
        self.action_group = build_action_group(self)
        self.action_group.get_action("reset-tool-after-create").set_active(
            self.properties.get("reset-tool-after-create", True)
        )

    def open(self):
        widget = self.construct()
        self.main_window.window.connect_after(
            "key-press-event", self._on_key_press_event
        )
        return widget

    def close(self):
        if self._toolbox:
            self._toolbox.destroy()
            self._toolbox = None

    def construct(self):
        toolbox = _Toolbox(TOOLBOX_ACTIONS)
        toolbox.show()

        toolbox.connect("destroy", self._on_toolbox_destroyed)
        self._toolbox = toolbox
        return toolbox

    def _on_key_press_event(self, view, event):
        """
        Grab top level window events and select the appropriate tool based on the event.
        """
        if event.get_state() & Gdk.ModifierType.SHIFT_MASK or (
            event.get_state() == 0 or event.get_state() & Gdk.ModifierType.MOD2_MASK
        ):
            keyval = Gdk.keyval_name(event.keyval)
            self.set_active_tool(shortcut=keyval)

    def _on_toolbox_destroyed(self, widget):
        self._toolbox = None

    @toggle_action(name="reset-tool-after-create", label=_("_Reset tool"), active=False)
    def reset_tool_after_create(self, active):
        self.properties.set("reset-tool-after-create", active)

    @component.adapter(IDiagramPageChange)
    def _on_diagram_page_change(self, event):
        self.update_toolbox(event.diagram_page.toolbox.action_group)

    def update_toolbox(self, action_group):
        """
        Update the buttons in the toolbox. Each button should be connected
        by an action. Each button is assigned a special _action_name_
        attribute that can be used to fetch the action from the ui manager.
        """
        if not self._toolbox:
            return

        for button in self._toolbox.buttons:

            action_name = button.action_name
            action = action_group.get_action(action_name)
            if action:
                button.set_related_action(action)

    def set_active_tool(self, action_name=None, shortcut=None):
        """
        Set the tool based on the name of the action
        """
        # HACK:
        toolbox = self._toolbox
        if shortcut and toolbox:
            action_name = toolbox.shortcuts.get(shortcut)
            log.debug("Action for shortcut %s: %s" % (shortcut, action_name))
            if not action_name:
                return


@implementer(IUIComponent, IActionProvider)
class Diagrams(object):

    title = _("Diagrams")
    placement = ("left", "diagrams")

    component_registry = inject("component_registry")
    properties = inject("properties")

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

    def open(self):
        """Open the diagrams component.

        Returns:
            The Gtk.Notebook.

        """
        self._notebook = Gtk.Notebook()
        self._notebook.show()
        self.component_registry.register_handler(self._on_show_diagram)
        return self._notebook

    def close(self):
        """Close the diagrams component.

        """
        self.component_registry.unregister_handler(self._on_show_diagram)
        self._notebook.destroy()
        self._notebook = None

    def get_current_diagram(self):
        """Returns the current page of the notebook.

        Returns (DiagramPage): The current diagram page.

        """
        page_num = self._notebook.get_current_page()
        child_widget = self._notebook.get_nth_page(page_num)
        return child_widget.diagram_page.get_diagram()

    def cb_close_tab(self, button, widget):
        """Callback to close the tab and remove the notebook page.

        Args:
            button (Gtk.Button): The button the callback is from.
            widget (Gtk.Widget): The child widget of the tab.

        """
        page_num = self._notebook.page_num(widget)
        # TODO why does Gtk.Notebook give a GTK-CRITICAL if you remove a page
        #   with set_show_tabs(True)?
        self._notebook.set_show_tabs(False)
        self._notebook.remove_page(page_num)
        if self._notebook.get_n_pages() > 0:
            self._notebook.set_show_tabs(True)
        widget.diagram_page.close()
        widget.destroy()

    def create_tab(self, title, widget):
        """Creates a new Notebook tab with a label and close button.

        Args:
            title (str): The title of the tab, the diagram name.
            widget (Gtk.Widget): The child widget of the tab.

        """
        tab_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        label = Gtk.Label(title)
        tab_box.pack_start(label)

        close_image = Gtk.Image.new_from_icon_name(
            icon_name="window-close", size=Gtk.IconSize.MENU
        )
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_focus_on_click(False)
        button.add(close_image)
        tab_box.pack_start(child=button, expand=False, fill=False, padding=0)
        tab_box.show_all()

        page_num = self._notebook.append_page(child=widget, tab_label=tab_box)
        self._notebook.set_current_page(page_num)
        self._notebook.set_tab_reorderable(widget, True)

        button.connect("clicked", self.cb_close_tab, widget)
        self.component_registry.handle(DiagramPageChange(widget))
        self._notebook.set_show_tabs(True)

    def get_widgets_on_pages(self):
        """Gets the widget on each open page Notebook page.

        The page is the page number in the Notebook (0 indexed) and the widget
        is the child widget on each page.

        Returns:
            List of tuples (page, widget) of the currently open Notebook pages.

        """
        widgets_on_pages = []
        num_pages = self._notebook.get_n_pages()
        for page in range(0, num_pages):
            widget = self._notebook.get_nth_page(page)
            widgets_on_pages.append((page, widget))
        return widgets_on_pages

    @component.adapter(Diagram)
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
        widget.set_name("diagram-tab")
        widget.diagram_page = page
        assert widget.get_name() == "diagram-tab"
        page.set_drawing_style(self.properties("diagram.sloppiness", 0))

        self.create_tab(diagram.name, widget)
        return page

    @toggle_action(name="diagram-drawing-style", label="Hand drawn style", active=False)
    def hand_drawn_style(self, active):
        """
        Toggle between straight diagrams and "hand drawn" diagram style.
        """
        if active:
            sloppiness = 0.5
        else:
            sloppiness = 0.0
        for page, widget in self.get_widgets_on_pages():
            widget.diagram_page.set_drawing_style(sloppiness)
        self.properties.set("diagram.sloppiness", sloppiness)
