"""
The main application window.
"""

import importlib.resources
import logging
from pathlib import Path
from typing import List, Tuple

from gi.repository import Gdk, Gio, Gtk

from gaphor import UML
from gaphor.abc import ActionProvider, Service
from gaphor.core import action, event_handler, gettext
from gaphor.event import ActionEnabled, ActiveSessionChanged, SessionShutdownRequested
from gaphor.services.undomanager import UndoManagerStateChanged
from gaphor.ui.abc import UIComponent
from gaphor.ui.actiongroup import window_action_group
from gaphor.ui.diagrampage import DiagramPage
from gaphor.ui.event import (
    DiagramClosed,
    DiagramOpened,
    DiagramSelectionChanged,
    FileLoaded,
    FileSaved,
    ProfileSelectionChanged,
)
from gaphor.ui.layout import deserialize
from gaphor.ui.recentfiles import HOME, RecentFilesMenu
from gaphor.UML.event import AttributeUpdated, ModelFlushed, ModelReady

log = logging.getLogger(__name__)


def new_builder():
    builder = Gtk.Builder()
    builder.set_translation_domain("gaphor")
    with importlib.resources.path("gaphor.ui", "mainwindow.glade") as glade_file:
        builder.add_from_file(str(glade_file))
    return builder


def create_hamburger_model(export_menu, tools_menu):
    model = Gio.Menu.new()

    part = Gio.Menu.new()
    part.append(gettext("New Window"), "app.file-new")
    part.append(gettext("New from Template"), "app.file-new-template")
    model.append_section(None, part)

    part = Gio.Menu.new()
    part.append(gettext("Save"), "win.file-save")
    part.append(gettext("Save As..."), "win.file-save-as")
    part.append_submenu(gettext("Export"), export_menu)
    model.append_section(None, part)

    part = Gio.Menu.new()
    part.append_submenu(gettext("Tools"), tools_menu)
    model.append_section(None, part)

    part = Gio.Menu.new()
    part.append(gettext("Preferences"), "win.preferences")
    part.append(gettext("Keyboard Shortcuts"), "app.shortcuts")
    part.append(gettext("About Gaphor"), "app.about")
    model.append_section(None, part)

    return model


def create_recent_files_model(recent_manager=None):
    model = Gio.Menu.new()
    model.append_section(
        gettext("Recently opened files"),
        RecentFilesMenu(recent_manager or Gtk.RecentManager.get_default()),
    )
    return model


class MainWindow(Service, ActionProvider):
    """
    The main window for the application.
    It contains a Namespace-based tree view and a menu and a statusbar.
    """

    size = property(lambda s: s.properties.get("ui.window-size", (760, 580)))

    def __init__(
        self,
        event_manager,
        component_registry,
        element_factory,
        properties,
        export_menu,
        tools_menu,
    ):
        self.event_manager = event_manager
        self.component_registry = component_registry
        self.element_factory = element_factory
        self.properties = properties
        self.export_menu = export_menu
        self.tools_menu = tools_menu

        self.title = "Gaphor"
        self.window: Gtk.Window = None
        self.filename = None
        self.model_changed = False
        self.layout = None

        self.init_styling()

    def init_styling(self):
        with importlib.resources.path("gaphor.ui", "layout.css") as css_file:
            style_provider = Gtk.CssProvider()
            style_provider.load_from_path(str(css_file))
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                style_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

    def shutdown(self):
        if self.window:
            self.window.destroy()
            self.window = None

        em = self.event_manager
        em.unsubscribe(self._on_file_manager_state_changed)
        em.unsubscribe(self._on_undo_manager_state_changed)
        em.unsubscribe(self._new_model_content)
        em.unsubscribe(self._on_action_enabled)

    def get_ui_component(self, name):
        return self.component_registry.get(UIComponent, name)

    def _factory(self, name):
        comp = self.get_ui_component(name)
        widget = comp.open()

        # Okay, this may be hackish. Action groups on component level are also added
        # to the main window. This ensures that we can call those items from the
        # (main) menus as well. Also this makes enabling/disabling work.
        for prefix in widget.list_action_prefixes():
            assert prefix not in ("app", "win")
            self.window.insert_action_group(prefix, widget.get_action_group(prefix))
        return widget

    def open(self, gtk_app=None):
        """Open the main window."""

        builder = new_builder()
        self.window = builder.get_object("main-window")
        self.window.set_application(gtk_app)

        profile_combo = builder.get_object("profile-combo")
        profile_combo.connect("changed", self._on_profile_selected)
        selected_profile = self.properties.get("profile", default="UML")
        profile_combo.set_active_id(selected_profile)

        hamburger = builder.get_object("hamburger")
        hamburger.bind_model(
            create_hamburger_model(self.export_menu.menu, self.tools_menu.menu), None
        )

        recent_files = builder.get_object("recent-files")
        recent_files.bind_model(create_recent_files_model(), None)

        self.set_title()

        self.window.set_default_size(*self.size)

        with importlib.resources.open_text("gaphor.ui", "layout.xml") as f:
            self.layout = deserialize(self.window, f.read(), self._factory)

        action_group, accel_group = window_action_group(self.component_registry)
        self.window.insert_action_group("win", action_group)
        self.window.add_accel_group(accel_group)

        self.window.show_all()

        self.window.connect("notify::is-active", self._on_window_active)
        self.window.connect("delete-event", self._on_window_delete)

        # We want to store the window size, so it can be reloaded on startup
        self.window.set_resizable(True)
        self.window.connect("size-allocate", self._on_window_size_allocate)

        em = self.event_manager
        em.subscribe(self._on_file_manager_state_changed)
        em.subscribe(self._on_undo_manager_state_changed)
        em.subscribe(self._new_model_content)
        em.subscribe(self._on_action_enabled)

    def open_welcome_page(self):
        """
        Create a new tab with a textual welcome page, a sort of 101 for
        Gaphor.
        """

    def set_title(self):
        """
        Sets the window title.
        """
        if self.window:
            if self.filename:
                p = Path(self.filename)
                title = p.name
                subtitle = str(p.parent).replace(HOME, "~")
            else:
                title = self.title
                subtitle = ""
            if self.model_changed:
                title += " [" + gettext("edited") + "]"
            self.window.set_title(title)
            self.window.get_titlebar().set_subtitle(subtitle)

    # Signal callbacks:

    @event_handler(ModelReady)
    def _new_model_content(self, event):
        """
        Open the toplevel element and load toplevel diagrams.
        """
        # TODO: Make handlers for ModelReady from within the GUI obj
        for diagram in self.element_factory.select(
            lambda e: e.isKindOf(UML.Diagram)
            and not (e.namespace and e.namespace.namespace)
        ):
            self.event_manager.handle(DiagramOpened(diagram))

    @event_handler(FileLoaded, FileSaved)
    def _on_file_manager_state_changed(self, event):
        self.model_changed = False
        self.filename = event.filename
        self.set_title()

    @event_handler(UndoManagerStateChanged)
    def _on_undo_manager_state_changed(self, event):
        """
        """
        undo_manager = event.service
        if self.model_changed != undo_manager.can_undo():
            self.model_changed = undo_manager.can_undo()
            self.set_title()

    @event_handler(ActionEnabled)
    def _on_action_enabled(self, event):
        ag = self.window.get_action_group(event.scope)
        a = ag.lookup_action(event.name)
        a.set_enabled(event.enabled)

    def _on_window_active(self, window, prop):
        self.event_manager.handle(ActiveSessionChanged(self))

    def _on_window_delete(self, window, event):
        self.event_manager.handle(SessionShutdownRequested(self))
        return True

    def _on_window_size_allocate(self, window, allocation):
        """
        Store the window size in a property.
        """
        width, height = window.get_size()
        self.properties.set("ui.window-size", (width, height))

    def _on_profile_selected(self, combo):
        """Store the selected profile in a property."""
        profile = combo.get_active_text()
        self.event_manager.handle(ProfileSelectionChanged(profile))
        self.properties.set("profile", profile)

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


class Diagrams(UIComponent, ActionProvider):

    title = gettext("Diagrams")

    def __init__(self, event_manager, element_factory, properties):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.properties = properties
        self._notebook: Gtk.Notebook = None

    def open(self):
        """Open the diagrams component.

        Returns:
            The Gtk.Notebook.
        """

        self._notebook = Gtk.Notebook()
        self._notebook.props.scrollable = True
        self._notebook.show()
        self._notebook.connect("switch-page", self._on_switch_page)
        self.event_manager.subscribe(self._on_show_diagram)
        self.event_manager.subscribe(self._on_close_diagram)
        self.event_manager.subscribe(self._on_name_change)
        self.event_manager.subscribe(self._on_flush_model)
        return self._notebook

    def close(self):
        """Close the diagrams component."""

        self.event_manager.unsubscribe(self._on_flush_model)
        self.event_manager.unsubscribe(self._on_name_change)
        self.event_manager.unsubscribe(self._on_close_diagram)
        self.event_manager.unsubscribe(self._on_show_diagram)
        if self._notebook:
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
        return child_widget and child_widget.diagram_page.get_view()

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

        view = widget.diagram_page.view
        self.event_manager.handle(
            DiagramSelectionChanged(view, view.focused_item, view.selected_items)
        )

    def tab_label(self, title, widget):
        tab_box = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        label = Gtk.Label.new(title)
        tab_box.pack_start(child=label, expand=True, fill=True, padding=0)

        close_image = Gtk.Image.new_from_icon_name(
            icon_name="window-close", size=Gtk.IconSize.BUTTON
        )
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)

        # TODO: Call button.set_focus_on_click directly once PyGObject issue
        #  #371 is fixed
        Gtk.Widget.set_focus_on_click(button, False)

        button.add(close_image)
        button.connect(
            "clicked",
            lambda _button: self.event_manager.handle(
                DiagramClosed(widget.diagram_page.get_diagram())
            ),
        )
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

        widgets_on_pages: List[Tuple[int, Gtk.Widget]] = []
        if not self._notebook:
            return widgets_on_pages

        num_pages = self._notebook.get_n_pages()
        for page_num in range(0, num_pages):
            widget = self._notebook.get_nth_page(page_num)
            widgets_on_pages.append((page_num, widget))
        return widgets_on_pages

    def _on_switch_page(self, notebook, page, new_page_num):
        current_page_num = notebook.get_current_page()
        if current_page_num >= 0:
            self._clear_ui_settings(notebook.get_nth_page(current_page_num))
        self._add_ui_settings(page)
        view = page.diagram_page.view
        self.event_manager.handle(
            DiagramSelectionChanged(view, view.focused_item, view.selected_items)
        )

    def _add_ui_settings(self, page):
        window = page.get_toplevel()
        window.insert_action_group("diagram", page.action_group.actions)
        window.add_accel_group(page.action_group.shortcuts)

    def _clear_ui_settings(self, page):
        window = page.get_toplevel()
        window.insert_action_group("diagram", None)
        window.remove_accel_group(page.action_group.shortcuts)

    @action(name="close-current-tab", shortcut="<Primary>w")
    def close_current_tab(self):
        diagram = self.get_current_diagram()
        self.event_manager.handle(DiagramClosed(diagram))

    @event_handler(DiagramOpened)
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
                self.get_current_view().grab_focus()
                return widget.diagram_page

        # No existing diagram page found, creating one
        page = DiagramPage(
            diagram, self.event_manager, self.element_factory, self.properties
        )
        widget = page.construct()
        widget.set_name("diagram-tab")
        widget.diagram_page = page
        page.set_drawing_style(self.properties.get("diagram.sloppiness", 0))

        self.create_tab(diagram.name, widget)
        self.get_current_view().grab_focus()
        return page

    @event_handler(DiagramClosed)
    def _on_close_diagram(self, event):
        """Callback to close the tab and remove the notebook page.

        Args:
            button (Gtk.Button): The button the callback is from.
            widget (Gtk.Widget): The child widget of the tab.
        """
        diagram = event.diagram

        for page_num, widget in self.get_widgets_on_pages():
            if widget.diagram_page.get_diagram() is diagram:
                break
        else:
            log.warn(f"No tab found for diagram {diagram}")
            return

        if diagram is self.get_current_diagram():
            self._clear_ui_settings(widget)
        self._notebook.remove_page(page_num)
        widget.diagram_page.close()
        widget.destroy()

    @event_handler(ModelFlushed)
    def _on_flush_model(self, event):
        """
        Close all tabs.
        """
        while self._notebook.get_n_pages():
            self._notebook.remove_page(0)

    @event_handler(AttributeUpdated)
    def _on_name_change(self, event):
        if event.property is UML.Diagram.name:
            for page in range(0, self._notebook.get_n_pages()):
                widget = self._notebook.get_nth_page(page)
                if event.element is widget.diagram_page.diagram:
                    self._notebook.set_tab_label(
                        widget, self.tab_label(event.new_value, widget)
                    )
