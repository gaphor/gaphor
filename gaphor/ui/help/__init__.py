"""About, preferences, and help services.

(help browser anyone?)
"""

import sys

from gi.repository import Adw, Gio, Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.application import distribution
from gaphor.core import action
from gaphor.i18n import get_available_ui_languages, gettext, translated_ui_string
from gaphor.settings import StyleVariant, settings
from gaphor.ui.help.debuginfo import DebugInfo


def new_builder(ui_file):
    builder = Gtk.Builder()
    builder.add_from_string(translated_ui_string("gaphor.ui.help", f"{ui_file}.ui"))
    return builder


class HelpService(Service, ActionProvider):
    def __init__(self, application):
        self.application = application
        self.preferences_dialog = None
        self.debug_info = DebugInfo(application)

    def shutdown(self):
        self.debug_info.shutdown()

    @property
    def window(self):
        return self.application.active_window

    @action(name="app.about")
    def about(self):
        builder = new_builder("about")
        about = builder.get_object("about")

        about.set_version(distribution().version)
        about.set_debug_info(self.debug_info.create_debug_info())
        about.present(self.window)
        return about

    @action(name="app.documentation", shortcut="F1")
    def documentation(self):
        Gio.AppInfo.launch_default_for_uri("https://docs.gaphor.org", None)

    @action(name="app.shortcuts", shortcut="<Primary>question")
    def shortcuts(self):
        builder = Gtk.Builder()
        ui = translated_ui_string("gaphor.ui.help", "shortcuts.ui")
        modifier = "Meta" if sys.platform == "darwin" else "Control"
        ui = ui.replace("&lt;Primary&gt;", f"&lt;{modifier}&gt;")

        builder.add_from_string(ui)

        shortcuts = builder.get_object("shortcuts-gaphor")
        shortcuts.present(self.window)
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
        if self.preferences_dialog:
            self.preferences_dialog.add_toast(
                Adw.Toast(
                    title=gettext("Restart Gaphor to enable language changes"),
                )
            )

    def _on_display_language_selected(self, combo_row: Adw.ComboRow, param) -> None:
        codes = getattr(self, "_display_language_codes", [])
        if not codes:
            return
        idx = combo_row.get_selected()
        if 0 <= idx < len(codes):
            settings.ui_language = codes[idx]
        if self.preferences_dialog:
            self.preferences_dialog.add_toast(
                Adw.Toast(
                    title=gettext("Restart Gaphor to enable language changes"),
                )
            )

    @action(name="app.preferences", shortcut="<Primary>comma")
    def preferences(self):
        builder = Gtk.Builder()
        ui = translated_ui_string("gaphor.ui.help", "preferences.ui")

        builder.add_from_string(ui)

        self.preferences_dialog = builder.get_object("preferences")

        style_variant: Adw.ComboRow = builder.get_object("style_variant")
        display_language: Adw.ComboRow = builder.get_object("display_language")
        use_english: Adw.SwitchRow = builder.get_object("use_english")
        reset_tool_after_create: Adw.SwitchRow = builder.get_object(
            "reset_tool_after_create"
        )
        remove_unused_elements: Adw.SwitchRow = builder.get_object(
            "remove_unused_elements"
        )

        # Populate display language combo from available locales
        ui_languages = get_available_ui_languages()
        self._display_language_codes = [code for code, _ in ui_languages]
        model = Gtk.StringList.new([name for _, name in ui_languages])
        display_language.set_model(model)
        try:
            selected_idx = self._display_language_codes.index(settings.ui_language)
        except ValueError:
            selected_idx = 0
        display_language.set_selected(selected_idx)
        display_language.connect("notify::selected", self._on_display_language_selected)

        settings.bind_use_english(use_english, "active")
        use_english.connect("notify::active", self._on_use_english_selected)

        settings.bind_style_variant(style_variant, "selected")
        style_variant.connect("notify::selected-item", self._on_style_variant_selected)

        settings.bind_reset_tool_after_create(reset_tool_after_create, "active")
        settings.bind_remove_unused_elements(remove_unused_elements, "active")

        self.preferences_dialog.present(self.window)
        return self.preferences_dialog
