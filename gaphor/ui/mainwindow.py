"""The main application window."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

from gi.repository import Gio, GLib, Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.application import distribution
from gaphor.core import action, event_handler, gettext
from gaphor.core.modeling import ModelReady
from gaphor.event import (
    ActionEnabled,
    ActiveSessionChanged,
    ModelSaved,
    Notification,
    SessionCreated,
    SessionShutdownRequested,
    TransactionClosed,
)
from gaphor.i18n import translated_ui_string
from gaphor.services.modelinglanguage import ModelingLanguageChanged
from gaphor.services.undomanager import UndoManagerStateChanged
from gaphor.ui import macos_menubar
from gaphor.ui.abc import UIComponent
from gaphor.ui.actiongroup import window_action_group
from gaphor.ui.event import CurrentDiagramChanged
from gaphor.ui.filedialog import pretty_path
from gaphor.ui.modelbrowser import create_diagram_types_model
from gaphor.ui.notification import InAppNotifier

log = logging.getLogger(__name__)


def new_builder():
    builder = Gtk.Builder()
    builder.add_from_string(translated_ui_string("gaphor.ui", "mainwindow.ui"))
    return builder


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

    def __init__(
        self,
        event_manager,
        component_registry,
        properties,
        modeling_language,
        export_menu,
        tools_menu,
    ):
        self.event_manager = event_manager
        self.component_registry = component_registry
        self.properties = properties
        self.modeling_language = modeling_language
        self.export_menu = export_menu
        self.tools_menu = tools_menu

        self._builder: Gtk.Builder | None = new_builder()
        self.window: Gtk.Window | None = None
        self.modeling_language_name = None
        self.diagram_types = None
        self.in_app_notifier = None

        # UI updates to be performed when the window is shown/open.
        self._ui_updates: list[Callable[[], None]] = []

        event_manager.subscribe(self._on_file_manager_state_changed)
        event_manager.subscribe(self._on_current_diagram_changed)
        event_manager.subscribe(self._on_model_ready)
        event_manager.subscribe(self._on_undo_manager_state_changed)
        event_manager.subscribe(self._on_action_enabled)
        event_manager.subscribe(self._on_modeling_language_selection_changed)
        event_manager.subscribe(self._on_notification)

    def shutdown(self):
        if self.window:
            self.window.destroy()
            self._builder = None
            self.in_app_notifier = None

        em = self.event_manager
        em.unsubscribe(self._on_file_manager_state_changed)
        em.unsubscribe(self._on_current_diagram_changed)
        em.unsubscribe(self._on_model_ready)
        em.unsubscribe(self._on_undo_manager_state_changed)
        em.unsubscribe(self._on_action_enabled)
        em.unsubscribe(self._on_modeling_language_selection_changed)
        em.unsubscribe(self._on_notification)

    @property
    def title(self):
        return self._builder.get_object("title") if self._builder else None

    @property
    def modified(self):
        return self._builder.get_object("modified") if self._builder else None

    @property
    def subtitle(self):
        return self._builder.get_object("subtitle") if self._builder else None

    @property
    def element_editor_overlay(self):
        return (
            self._builder.get_object("element-editor-overlay")
            if self._builder
            else None
        )

    @property
    def model_changed(self) -> bool:
        return self.modified.get_visible() if self.modified else False

    @model_changed.setter
    def model_changed(self, model_changed: bool):
        if self.modified:
            self.modified.set_visible(model_changed)

    def open(self, gtk_app=None):
        """Open the main window."""

        builder = self._builder
        assert builder

        if not self.window:
            self.window = builder.get_object("main-window")

        window = self.window
        window.set_application(gtk_app)
        if ".dev" in distribution().version:
            window.add_css_class("devel")

        select_modeling_language = builder.get_object("select-modeling-language")
        select_modeling_language.set_menu_model(
            create_modeling_language_model(self.modeling_language)
        )
        self.modeling_language_name = builder.get_object("modeling-language-name")

        self.diagram_types = builder.get_object("diagram-types")
        self.diagram_types.set_menu_model(
            create_diagram_types_model(self.modeling_language)
        )

        if macos_menubar():
            builder.get_object("hamburger-menu-button").unparent()
        else:
            builder.get_object("export-menu").append_submenu(
                gettext("Export"), self.export_menu.menu
            )
            builder.get_object("tools-menu").append_submenu(
                gettext("Tools"), self.tools_menu.menu
            )

        window.set_default_size(*(self.properties.get("ui.window-size", (1024, 640))))
        window_mode = self.properties.get("ui.window-mode", "")
        if window_mode == "maximized":
            window.maximize()
        elif window_mode == "fullscreened":
            window.fullscreen()

        track_paned_position(
            builder.get_object("left-pane"), "ui.namespace-width", self.properties
        )

        track_paned_position(
            builder.get_object("top-left-pane"), "ui.namespace-height", self.properties
        )

        if overlay := self.element_editor_overlay:
            overlay.set_show_sidebar(self.properties.get("show-editors", True))

        for name, component in self.component_registry.all(UIComponent):
            if bin := builder.get_object(f"component:{name}"):
                widget = component.open()
                widget.set_name(name)
                bin.set_child(widget)

        action_groups = {
            "win": window_action_group(self.component_registry),
            "text": window_action_group(self.component_registry, scope="text"),
        }
        for scope, action_group in action_groups.items():
            window.insert_action_group(scope, action_group)

        self._on_modeling_language_selection_changed()
        self.in_app_notifier = InAppNotifier(builder.get_object("main-overlay"))

        window.connect("close-request", self._on_window_close_request)
        window.connect("notify::default-height", self._on_window_size_changed)
        window.connect("notify::default-width", self._on_window_size_changed)
        window.connect("notify::maximized", self._on_window_mode_changed)
        window.connect("notify::fullscreened", self._on_window_mode_changed)
        window.connect("notify::is-active", self._on_window_active)
        window.connect("notify::focus-widget", self._on_window_focus_widget)
        window.present()

        for handler in self._ui_updates:
            handler()
        del self._ui_updates[:]

    # Actions:

    @action(
        name="show-editors",
        shortcut="F9",
        state=lambda self: self.properties.get("show-editors", True),
    )
    def toggle_editor_visibility(self, active):
        if overlay := self.element_editor_overlay:
            overlay.set_show_sidebar(active)
        self.properties.set("show-editors", active)

    @action("maximize", state=lambda self: self.window.is_maximized())
    def toggle_maximized(self, active):
        if not self.window:
            return

        if active:
            self.window.maximize()
        else:
            self.window.unmaximize()

    @action(
        "fullscreen", shortcut="F11", state=lambda self: self.window.is_fullscreen()
    )
    def toggle_fullscreen(self, active):
        if not self.window:
            return

        if active:
            self.window.fullscreen()
            self.event_manager.handle(
                Notification(gettext("Press F11 to exit Fullscreen"))
            )
        else:
            self.window.unfullscreen()

    # Signal callbacks:

    @event_handler(SessionCreated, ModelSaved)
    def _on_file_manager_state_changed(
        self, event: SessionCreated | ModelSaved
    ) -> None:
        if not (window := self.window):
            self._ui_updates.append(lambda: self._on_file_manager_state_changed(event))
            return

        filename = Path(event.filename) if event.filename else None

        self.subtitle.set_text(
            pretty_path(filename) if filename else gettext("New model")
        )
        window.set_title(
            f"{filename.name} ({pretty_path(filename.parent)}) - Gaphor"
            if filename
            else f"{gettext('New model')} - Gaphor"
        )

        self.model_changed = False

        window.present()

    @event_handler(ModelReady)
    def _on_model_ready(self, event: ModelReady):
        self.model_changed = event.modified

    @event_handler(CurrentDiagramChanged)
    def _on_current_diagram_changed(self, event):
        self.title.set_text(
            (event.diagram.name or gettext("<None>")) if event.diagram else "Gaphor"
        )

    @event_handler(UndoManagerStateChanged)
    def _on_undo_manager_state_changed(self, event: UndoManagerStateChanged):
        self.model_changed = True

    @event_handler(ActionEnabled)
    def _on_action_enabled(self, event):
        if self.window:
            self.window.action_set_enabled(event.action_name, event.enabled)
            if self._builder and event.action_name == "win.diagram-align":
                self._builder.get_object("alignment-button").set_sensitive(
                    event.enabled
                )
        else:
            self._ui_updates.append(lambda: self._on_action_enabled(event))

    @event_handler(ModelingLanguageChanged)
    def _on_modeling_language_selection_changed(self, event=None):
        if self.modeling_language_name:
            self.modeling_language_name.set_label(self.modeling_language.name)
        if self.diagram_types:
            self.diagram_types.set_menu_model(
                create_diagram_types_model(self.modeling_language)
            )

    @event_handler(Notification)
    def _on_notification(self, event: Notification):
        if not self.in_app_notifier:
            self._ui_updates.append(lambda: self._on_notification(event))
            return

        self.in_app_notifier.handle(event)

    def _on_window_active(self, window, _prop):
        app = window.get_application()
        app.update_menu("export", self.export_menu.menu)
        app.update_menu("tools", self.tools_menu.menu)
        self.event_manager.handle(ActiveSessionChanged(self))

    def _on_window_focus_widget(self, _window, _prop):
        self.event_manager.handle(TransactionClosed())

    def _on_window_close_request(self, _window, _event=None):
        self.event_manager.handle(SessionShutdownRequested(quitting=False))
        return True

    def _on_window_size_changed(self, window, _gspec):
        if not is_maximized(window):
            width, height = window.get_default_size()
            self.properties.set("ui.window-size", (width, height))

    def _on_window_mode_changed(self, window, gspec):
        mode = gspec.name
        self.properties.set("ui.window-mode", mode if window.get_property(mode) else "")


def is_maximized(window: Gtk.Window) -> bool:
    return window.is_maximized() or window.is_fullscreen()  # type: ignore[no-any-return]


def _paned_position_changed(paned, _gparam, name, properties):
    if not is_maximized(paned.get_root()):
        properties.set(name, paned.props.position)


def _paned_ensure_visible(paned, _gparam):
    if paned.props.position < paned.props.min_position + 12:
        paned.props.position = paned.props.min_position + 12
    elif paned.props.position > paned.props.max_position - 12:
        paned.props.position = paned.props.max_position - 12


def track_paned_position(paned, name, properties):
    paned.connect("notify::position", _paned_ensure_visible)
    paned.connect("notify::min-position", _paned_ensure_visible)
    paned.connect("notify::max-position", _paned_ensure_visible)

    if position := properties.get(name, 0):
        paned.set_position(position)

    paned.connect("notify::position", _paned_position_changed, name, properties)
