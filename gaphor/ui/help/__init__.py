"""About, preferences, and help services.

(help browser anyone?)
"""
import logging
import sys
import webbrowser

from gi.repository import Adw, GObject, Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.application import distribution
from gaphor.core import action
from gaphor.i18n import gettext, translated_ui_string
from gaphor.settings import StyleVariant, settings

logger = logging.getLogger(__name__)


def new_builder(ui_file):
    builder = Gtk.Builder()
    builder.add_from_string(translated_ui_string("gaphor.ui.help", f"{ui_file}.ui"))
    return builder


class HelpService(Service, ActionProvider):
    def __init__(self, application):
        self.application = application
        self.preferences_window = None

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

    def _on_style_variant_selected(self, combo_row: Adw.ComboRow, param) -> None:
        if self.application.gtk_app:
            selected = combo_row.props.selected_item
            if selected.props.string == "Dark":
                settings.style_variant = StyleVariant.DARK
            elif selected.props.string == "Light":
                settings.style_variant = StyleVariant.LIGHT
            else:
                settings.style_variant = StyleVariant.SYSTEM

    def _on_use_english_selected(self, switch_row: Adw.SwitchRow, param) -> None:
        if self.preferences_window:
            self.preferences_window.add_toast(
                Adw.Toast(
                    title=gettext("Restart Gaphor to enable language changes"),
                )
            )

    @action(name="app.preferences", shortcut="<Primary>comma")
    def preferences(self):
        builder = Gtk.Builder()
        ui = translated_ui_string("gaphor.ui.help", "preferences.ui")

        builder.add_from_string(ui)

        self.preferences_window = builder.get_object("preferences")
        self.preferences_window.set_modal(True)
        self.preferences_window.set_transient_for(self.window)

        style_variant: Adw.ComboRow = builder.get_object("style_variant")
        use_english: Adw.SwitchRow = builder.get_object("use_english")

        settings.bind_use_english(use_english, "active")
        use_english.connect("notify::active", self._on_use_english_selected)

        settings.bind_style_variant(style_variant, "selected")
        style_variant.connect("notify::selected-item", self._on_style_variant_selected)

        self.preferences_window.set_visible(True)
        return self.preferences_window


def activate_link(window, uri):
    """D-Bus does not work on macOS, so we open URL's ourselves."""
    if sys.platform == "darwin":
        GObject.signal_stop_emission_by_name(window, "activate-link")
        webbrowser.open(uri)
