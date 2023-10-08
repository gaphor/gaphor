"""About, preferences, and help services.

(help browser anyone?)
"""
import logging

import webbrowser
import sys
from enum import Enum

from gi.repository import Adw, Gio, GObject, Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.application import distribution
from gaphor.core import action
from gaphor.i18n import translated_ui_string
from gaphor.ui import APPLICATION_ID


logger = logging.getLogger(__name__)


class StyleValue(Enum):
    SYSTEM = 0
    DARK = 1
    LIGHT = 2


def new_builder(ui_file):
    builder = Gtk.Builder()
    builder.add_from_string(translated_ui_string("gaphor.ui.help", f"{ui_file}.ui"))
    return builder


def get_settings() -> Gio.Settings | None:
    """Get the Gio Settings for Gaphor."""
    schemas = Gio.Settings.list_schemas()
    if APPLICATION_ID in schemas:
        return Gio.Settings(schema_id=APPLICATION_ID)
    logger.info(
        "Settings schema not found and settings won't be saved, run `poe install-schemas`"
    )
    return None


class HelpService(Service, ActionProvider):
    def __init__(self, application):
        self.application = application
        self.settings = get_settings()
        if self.settings:
            self.style_variant = StyleValue(self.settings.get_enum("style-variant"))
            self._set_style_variant(self.style_variant)

    def shutdown(self):
        pass

    @property
    def window(self):
        return self.application.active_window

    @action(name="app.about")
    def about(self):
        builder = new_builder("about")
        about = builder.get_object("about")

        about.set_version(distribution().version)
        about.set_transient_for(self.window)
        about.connect("activate-link", activate_link)
        about.set_modal(True)
        about.set_visible(True)

    @action(name="app.shortcuts", shortcut="<Primary>question")
    def shortcuts(self):
        builder = Gtk.Builder()
        ui = translated_ui_string("gaphor.ui.help", "shortcuts.ui")
        modifier = "Meta" if sys.platform == "darwin" else "Control"
        ui = ui.replace("&lt;Primary&gt;", f"&lt;{modifier}&gt;")

        builder.add_from_string(ui)

        shortcuts = builder.get_object("shortcuts-gaphor")
        shortcuts.set_modal(True)
        shortcuts.set_transient_for(self.window)

        shortcuts.set_visible(True)
        return shortcuts

    def _on_dark_mode_selected(self, combo_row: Adw.ComboRow, param) -> None:
        selected = combo_row.props.selected_item
        if selected.props.string == "Dark":
            self._set_style_variant(StyleValue.DARK)
        elif selected.props.string == "Light":
            self._set_style_variant(StyleValue.LIGHT)
        else:
            self._set_style_variant(StyleValue.SYSTEM)

    def _set_style_variant(self, style_value: StyleValue) -> None:
        if gtk_app := self.application.gtk_app:
            style_manager = gtk_app.get_style_manager()
            if style_value == StyleValue.DARK:
                style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
            elif style_value == StyleValue.LIGHT:
                style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
            elif style_value == StyleValue.SYSTEM:
                style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)
        if self.settings:
            self.settings.set_enum("style-variant", style_value.value)

    @action(name="app.preferences", shortcut="<Primary>comma")
    def preferences(self):
        builder = Gtk.Builder()
        ui = translated_ui_string("gaphor.ui.help", "preferences.ui")

        builder.add_from_string(ui)

        preferences = builder.get_object("preferences")
        preferences.set_modal(True)
        preferences.set_transient_for(self.window)

        dark_mode_selection = builder.get_object("dark_mode_selection")
        use_english = builder.get_object("use_english")

        if self.settings:
            self.settings.bind(
                "use-english", use_english, "active", Gio.SettingsBindFlags.DEFAULT
            )

            # Bind with mapping not supported by PyGObject: https://gitlab.gnome.org/GNOME/pygobject/-/issues/98
            # To bind to a function that can map between guint and a string
            self.style_variant = self.settings.get_enum("style-variant")
            dark_mode_selection.set_selected(self.style_variant)

        dark_mode_selection.connect(
            "notify::selected-item", self._on_dark_mode_selected
        )

        preferences.set_visible(True)
        return preferences


def activate_link(window, uri):
    """D-Bus does not work on macOS, so we open URL's ourselves.
    """
    if sys.platform == "darwin":
        GObject.signal_stop_emission_by_name(window, "activate-link")
        webbrowser.open(uri)
