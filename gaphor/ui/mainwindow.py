"""The main application window."""

import importlib.resources
import logging
from pathlib import Path

from gi.repository import Gdk, Gio, GLib, Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.core import event_handler, gettext
from gaphor.core.modeling import Diagram, ModelReady
from gaphor.event import ActionEnabled, ActiveSessionChanged, SessionShutdownRequested
from gaphor.services.undomanager import UndoManagerStateChanged
from gaphor.ui.abc import UIComponent
from gaphor.ui.actiongroup import window_action_group
from gaphor.ui.event import (
    DiagramOpened,
    FileLoaded,
    FileSaved,
    ModelingLanguageChanged,
)
from gaphor.ui.layout import deserialize
from gaphor.ui.notification import InAppNotifier
from gaphor.ui.recentfiles import HOME, RecentFilesMenu

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


def create_modeling_language_model(modeling_language):
    model = Gio.Menu.new()
    for id, name in modeling_language.modeling_languages:
        menu_item = Gio.MenuItem.new(name, "win.select-modeling-language")
        menu_item.set_attribute_value("target", GLib.Variant.new_string(id))
        model.append_item(menu_item)
    return model


class MainWindow(Service, ActionProvider):
    """The main window for the application.

    It contains a Namespace-based tree view and a menu and a statusbar.
    """

    size = property(lambda s: s.properties.get("ui.window-size", (760, 580)))

    def __init__(
        self,
        event_manager,
        component_registry,
        element_factory,
        properties,
        modeling_language,
        export_menu,
        tools_menu,
    ):
        self.event_manager = event_manager
        self.component_registry = component_registry
        self.element_factory = element_factory
        self.properties = properties
        self.modeling_language = modeling_language
        self.export_menu = export_menu
        self.tools_menu = tools_menu

        self.title = "Gaphor"
        self.window: Gtk.Window = None
        self.filename = None
        self.model_changed = False
        self.layout = None
        self.modeling_language_name = None
        self.in_app_notifier = None

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
        em.unsubscribe(self._on_modeling_language_selection_changed)
        if self.in_app_notifier:
            em.unsubscribe(self.in_app_notifier.handle)
            self.in_app_notifier = None

    def get_ui_component(self, name):
        return self.component_registry.get(UIComponent, name)

    def open(self, gtk_app=None):
        """Open the main window."""

        builder = new_builder()
        self.window = builder.get_object("main-window")
        self.window.set_application(gtk_app)

        select_modeling_language = builder.get_object("select-modeling-language")
        select_modeling_language.bind_model(
            create_modeling_language_model(self.modeling_language), None
        )
        self.modeling_language_name = builder.get_object("modeling-language-name")

        hamburger = builder.get_object("hamburger")
        hamburger.bind_model(
            create_hamburger_model(self.export_menu.menu, self.tools_menu.menu), None
        )

        recent_files = builder.get_object("recent-files")
        recent_files.bind_model(create_recent_files_model(), None)

        self.set_title()

        self.window.set_default_size(*self.size)

        def _factory(name):
            comp = self.get_ui_component(name)
            widget = comp.open()

            # Okay, this may be hackish. Action groups on component level are also added
            # to the main window. This ensures that we can call those items from the
            # (main) menus as well. Also this makes enabling/disabling work.
            for prefix in widget.list_action_prefixes():
                assert prefix not in ("app", "win")
                self.window.insert_action_group(prefix, widget.get_action_group(prefix))
            return widget

        with importlib.resources.open_text("gaphor.ui", "layout.xml") as f:
            main_content = builder.get_object("main-content")
            self.layout = deserialize(main_content, f.read(), _factory, self.properties)

        action_group, accel_group = window_action_group(self.component_registry)
        self.window.insert_action_group("win", action_group)
        self.window.add_accel_group(accel_group)

        self._on_modeling_language_selection_changed()

        self.window.show_all()

        self.window.connect("notify::is-active", self._on_window_active)
        self.window.connect("delete-event", self._on_window_delete)

        # We want to store the window size, so it can be reloaded on startup
        self.window.set_resizable(True)
        self.window.connect("size-allocate", self._on_window_size_allocate)

        self.in_app_notifier = InAppNotifier(builder)
        em = self.event_manager
        em.subscribe(self._on_file_manager_state_changed)
        em.subscribe(self._on_undo_manager_state_changed)
        em.subscribe(self._new_model_content)
        em.subscribe(self._on_action_enabled)
        em.subscribe(self._on_modeling_language_selection_changed)
        em.subscribe(self.in_app_notifier.handle)

    def open_welcome_page(self):
        """Create a new tab with a textual welcome page, a sort of 101 for
        Gaphor."""

    def set_title(self):
        """Sets the window title."""
        if not self.window:
            return

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
        """Open the toplevel element and load toplevel diagrams."""
        for diagram in self.element_factory.select(
            lambda e: e.isKindOf(Diagram)
            and not (e.namespace and e.namespace.namespace)
        ):
            self.event_manager.handle(DiagramOpened(diagram))

    @event_handler(FileLoaded, FileSaved)
    def _on_file_manager_state_changed(self, event):
        self.model_changed = False
        self.filename = event.filename
        self.set_title()
        if self.window:
            self.window.present()

    @event_handler(UndoManagerStateChanged)
    def _on_undo_manager_state_changed(self, event):
        undo_manager = event.service
        if self.model_changed != undo_manager.can_undo():
            self.model_changed = undo_manager.can_undo()
            self.set_title()

    @event_handler(ActionEnabled)
    def _on_action_enabled(self, event):
        ag = self.window.get_action_group(event.scope)
        a = ag.lookup_action(event.name)
        a.set_enabled(event.enabled)

    @event_handler(ModelingLanguageChanged)
    def _on_modeling_language_selection_changed(self, event=None):
        if self.modeling_language_name:
            self.modeling_language_name.set_text(
                gettext("Profile: {}").format(
                    self.modeling_language.active_modeling_language_name
                )
            )

    def _on_window_active(self, window, prop):
        self.event_manager.handle(ActiveSessionChanged(self))

    def _on_window_delete(self, window, event):
        self.event_manager.handle(SessionShutdownRequested(self))
        return True

    def _on_window_size_allocate(self, window, allocation):
        """Store the window size in a property."""
        width, height = window.get_size()
        self.properties.set("ui.window-size", (width, height))


Gtk.AccelMap.add_filter("gaphor")
