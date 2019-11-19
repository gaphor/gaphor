import importlib

from gi.repository import Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.core import action
from gaphor.ui.actiongroup import create_action_group, set_action_state


class Shortcuts(Service, ActionProvider):
    def __init__(self, main_window, properties):
        self.main_window = main_window

    @action(name="app.shortcuts")
    def open(self):
        builder = Gtk.Builder()
        with importlib.resources.path("gaphor.ui", "shortcuts.glade") as glade_file:
            builder.add_objects_from_file(str(glade_file), ("shortcuts-gaphor",))

        shortcuts = builder.get_object("shortcuts-gaphor")
        shortcuts.set_transient_for(self.main_window.window)

        shortcuts.show_all()
        return shortcuts

    def shutdown(self):
        pass
