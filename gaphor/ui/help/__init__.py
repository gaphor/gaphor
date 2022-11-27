"""About and help services.

(help browser anyone?)
"""

from gi.repository import Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.application import distribution
from gaphor.core import action
from gaphor.i18n import translated_ui_string


def new_builder(ui_file):
    builder = Gtk.Builder()
    ui_file = f"{ui_file}.glade" if Gtk.get_major_version() == 3 else f"{ui_file}.ui"
    builder.add_from_string(translated_ui_string("gaphor.ui.help", ui_file))
    return builder


class HelpService(Service, ActionProvider):
    def __init__(self, main_window):
        self.main_window = main_window

    def shutdown(self):
        pass

    @property
    def window(self):
        return self.main_window.window

    @action(name="about")
    def about(self):
        builder = new_builder("about")
        about = builder.get_object("about")

        about.set_version(distribution().version)
        about.set_transient_for(self.window)

        if Gtk.get_major_version() == 3:
            about.run()
            about.destroy()
        else:
            about.set_modal(True)
            about.show()

    @action(name="win.shortcuts")
    def shortcuts(self):
        builder = Gtk.Builder()
        builder.add_from_string(translated_ui_string("gaphor.ui.help", "shortcuts.ui"))

        shortcuts = builder.get_object("shortcuts-gaphor")
        shortcuts.set_modal(True)
        shortcuts.set_transient_for(self.window)

        shortcuts.show()
        return shortcuts
