"""The main application window."""

from __future__ import annotations

import importlib.resources
import logging
from pathlib import Path
from typing import Callable

from gi.repository import Gio, GLib, Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.application import distribution
from gaphor.core import event_handler, gettext
from gaphor.event import (
    ActionEnabled,
    ActiveSessionChanged,
    ModelLoaded,
    ModelSaved,
    SessionShutdownRequested,
)
from gaphor.i18n import translated_ui_string
from gaphor.services.modelinglanguage import ModelingLanguageChanged
from gaphor.services.undomanager import UndoManagerStateChanged
from gaphor.ui.abc import UIComponent
from gaphor.ui.actiongroup import window_action_group
from gaphor.ui.event import CurrentDiagramChanged
from gaphor.ui.layout import deserialize, is_maximized
from gaphor.ui.modelbrowser import create_diagram_types_model
from gaphor.ui.notification import InAppNotifier

log = logging.getLogger(__name__)


def new_builder():
    builder = Gtk.Builder()
    builder.add_from_string(translated_ui_string("gaphor.ui", "mainwindow.ui"))
    return builder


def create_hamburger_model(export_menu, tools_menu):
    model = Gio.Menu.new()

    part = Gio.Menu.new()
    part.append(gettext("New Model…"), "app.new-model")
    part.append(gettext("Open Model…"), "app.file-open")
    model.append_section(None, part)

    part = Gio.Menu.new()
    part.append(gettext("Save"), "win.file-save")
    part.append(gettext("Save As…"), "win.file-save-as")
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

    size = property(lambda s: s.properties.get("ui.window-size", (860, 580)))

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
        self.action_group: Gio.ActionGroup = None
        self.modeling_language_name = None
        self.diagram_types = None
        self.in_app_notifier = None

        # UI updates to be performed when the window is shown/open.
        self._ui_updates: list[Callable[[], None]] = []

        event_manager.subscribe(self._on_file_manager_state_changed)
        event_manager.subscribe(self._on_current_diagram_changed)

    def shutdown(self):
        if self.window:
            self.window.destroy()
            self._builder = None

        em = self.event_manager
        em.unsubscribe(self._on_file_manager_state_changed)
        em.unsubscribe(self._on_current_diagram_changed)
        em.unsubscribe(self._on_undo_manager_state_changed)
        em.unsubscribe(self._on_action_enabled)
        em.unsubscribe(self._on_modeling_language_selection_changed)
        if self.in_app_notifier:
            em.unsubscribe(self.in_app_notifier.handle)
            self.in_app_notifier = None

    @property
    def window(self):
        return self._builder.get_object("main-window") if self._builder else None

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
    def model_changed(self) -> bool:
        return self.modified.get_visible() if self.modified else False  # type: ignore[no-any-return]

    @model_changed.setter
    def model_changed(self, model_changed: bool):
        if self.modified:
            self.modified.set_visible(model_changed)

    def get_ui_component(self, name):
        return self.component_registry.get(UIComponent, name)

    def open(self, gtk_app=None):
        """Open the main window."""

        builder = self._builder
        assert builder
        window = self.window
        window.set_application(gtk_app)
        if ".dev" in distribution().version:
            window.get_style_context().add_class("devel")

        select_modeling_language = builder.get_object("select-modeling-language")
        select_modeling_language.set_menu_model(
            create_modeling_language_model(self.modeling_language),
        )
        self.modeling_language_name = builder.get_object("modeling-language-name")

        self.diagram_types = builder.get_object("diagram-types")
        self.diagram_types.set_menu_model(
            create_diagram_types_model(self.modeling_language)
        )

        hamburger = builder.get_object("hamburger")
        hamburger.set_menu_model(
            create_hamburger_model(self.export_menu.menu, self.tools_menu.menu),
        )

        window.set_default_size(*self.size)

        def _factory(name):
            comp = self.get_ui_component(name)
            return comp.open()

        main_content = builder.get_object("main-content")
        deserialize(
            main_content,
            (importlib.resources.files("gaphor.ui") / "layout.xml").read_text(
                encoding="utf-8"
            ),
            _factory,
            self.properties,
        )

        self.action_group, shortcuts = window_action_group(self.component_registry)
        window.insert_action_group("win", self.action_group)

        self._on_modeling_language_selection_changed()

        window.set_resizable(True)
        window.add_controller(Gtk.ShortcutController.new_for_model(shortcuts))
        window.connect("close-request", self._on_window_close_request)
        window.connect("notify::default-height", self._on_window_size_changed)
        window.connect("notify::default-width", self._on_window_size_changed)
        window.show()

        window.connect("notify::is-active", self._on_window_active)

        self.in_app_notifier = InAppNotifier(builder)
        em = self.event_manager
        em.subscribe(self._on_undo_manager_state_changed)
        em.subscribe(self._on_action_enabled)
        em.subscribe(self._on_modeling_language_selection_changed)
        em.subscribe(self.in_app_notifier.handle)

        for handler in self._ui_updates:
            handler()
        del self._ui_updates[:]

    # Signal callbacks:

    @event_handler(ModelLoaded, ModelSaved)
    def _on_file_manager_state_changed(self, event: ModelLoaded | ModelSaved) -> None:
        if not (window := self.window):
            self._ui_updates.append(lambda: self._on_file_manager_state_changed(event))  # type: ignore[no-any-return]
            return

        filename = Path(event.filename) if event.filename else None

        self.subtitle.set_text(
            str(filename).replace(str(Path.home()), "~")
            if filename
            else gettext("New model")
        )
        window.set_title(
            f"{filename.name} ({str(filename.parent).replace(str(Path.home()), '~')}) - Gaphor"
            if filename
            else f"{gettext('New model')} - Gaphor"
        )

        self.model_changed = isinstance(event, ModelLoaded) and event.modified

        window.present()

    @event_handler(CurrentDiagramChanged)
    def _on_current_diagram_changed(self, event):
        if not self.window:
            self._ui_updates.append(lambda: self._on_current_diagram_changed(event))  # type: ignore[no-any-return]
            return

        self.title.set_text(
            (event.diagram.name or gettext("<None>")) if event.diagram else "Gaphor"
        )

    @event_handler(UndoManagerStateChanged)
    def _on_undo_manager_state_changed(self, event):
        undo_manager = event.service
        self.model_changed = undo_manager.can_undo()

    @event_handler(ActionEnabled)
    def _on_action_enabled(self, event):
        if self.action_group and event.scope == "win":
            a = self.action_group.lookup_action(event.name)
            a.set_enabled(event.enabled)

    @event_handler(ModelingLanguageChanged)
    def _on_modeling_language_selection_changed(self, event=None):
        if self.modeling_language_name:
            self.modeling_language_name.set_label(
                gettext("Profile: {name}").format(name=self.modeling_language.name)
            )
        if self.diagram_types:
            self.diagram_types.set_menu_model(
                create_diagram_types_model(self.modeling_language)
            )

    def _on_window_active(self, window, prop):
        self.event_manager.handle(ActiveSessionChanged(self))

    def _on_window_close_request(self, window, event=None):
        self.event_manager.handle(SessionShutdownRequested(self))
        return True

    def _on_window_size_changed(self, window, gspec):
        if not is_maximized(window):
            width, height = window.get_default_size()
            self.properties.set("ui.window-size", (width, height))
