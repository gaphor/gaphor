"""About, preferences, and help services.

(help browser anyone?)
"""

import webbrowser
import sys

from gi.repository import Adw, GObject, Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.application import distribution
from gaphor.core import action
from gaphor.i18n import translated_ui_string


def new_builder(ui_file):
    builder = Gtk.Builder()
    builder.add_from_string(translated_ui_string("gaphor.ui.help", f"{ui_file}.ui"))
    return builder


class HelpService(Service, ActionProvider):
    def __init__(self, application):
        self.application = application

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

    def _on_dark_mode_selected(self, dropdown, param):
        style_manager = self.application.gtk_app.get_style_manager()
        selected = dropdown.props.selected_item
        if selected.props.string == "Dark":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        elif selected.props.string == "Light":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

    @action(name="app.preferences", shortcut="<Primary>comma")
    def preferences(self):
        builder = Gtk.Builder()
        ui = translated_ui_string("gaphor.ui.help", "preferences.ui")

        builder.add_from_string(ui)

        preferences = builder.get_object("preferences")
        preferences.set_modal(True)
        preferences.set_transient_for(self.window)

        dark_mode_selection = builder.get_object("dark_mode_selection")
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
