import importlib

from gi.repository import Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.action import action, init_action_state
from gaphor.ui.actiongroup import create_action_group


class Preferences(Service, ActionProvider):
    def __init__(self, main_window, properties):
        self.main_window = main_window
        self.properties = properties

    @action(name="win.preferences", shortcut="<Primary>comma")
    def open(self):
        builder = Gtk.Builder()
        with importlib.resources.path("gaphor.ui", "mockups.glade") as glade_file:
            builder.add_objects_from_file(str(glade_file), ("preferences",))

        prefs = builder.get_object("preferences")
        prefs.set_transient_for(self.main_window.window)
        prefs.set_modal(True)

        prefs.insert_action_group("pref", self.create_action_group())

        prefs.show_all()
        return prefs

    def shutdown(self):
        pass

    def create_action_group(self):
        init_action_state(
            Preferences.hand_drawn_style,
            self.properties.get("diagram.sloppiness", 0.0) > 0.0,
        )
        init_action_state(
            Preferences.reset_tool_after_create,
            self.properties.get("reset-tool-after-create", True),
        )
        action_group, accel_group = create_action_group(self, "pref")
        return action_group

    @action(name="pref.hand-drawn-style", state=False)
    def hand_drawn_style(self, active):
        """Toggle between straight diagrams and "hand drawn" diagram style."""

        if active:
            sloppiness = 0.5
        else:
            sloppiness = 0.0
        self.properties.set("diagram.sloppiness", sloppiness)

    @action(name="pref.reset-tool-after-create", state=True)
    def reset_tool_after_create(self, active):
        self.properties.set("reset-tool-after-create", active)
