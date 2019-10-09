import importlib
from gi.repository import GLib, Gio, Gtk

from gaphor.abc import Service, ActionProvider
from gaphor.core import action
from gaphor.ui.actiongroup import create_action_group, set_action_state


class Preferences(Service, ActionProvider):
    def __init__(self, main_window, properties):
        self.main_window = main_window
        self.properties = properties

    @action(name="app.preferences")
    def open(self):
        # self.hand_drawn_style.active = self.properties.get("diagram.sloppiness", 0.0) > 0.0

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
        action_group, accel_group = create_action_group(self, "pref")

        set_action_state(
            action_group,
            "hand-drawn-style",
            self.properties.get("diagram.sloppiness", 0.0) > 0.0,
        )

        set_action_state(
            action_group,
            "reset-tool-after-create",
            self.properties.get("reset-tool-after-create", True),
        )
        return action_group

    @action(name="pref.hand-drawn-style", state=False)
    def hand_drawn_style(self, active: bool):
        """Toggle between straight diagrams and "hand drawn" diagram style."""

        if active:
            sloppiness = 0.5
        else:
            sloppiness = 0.0
        self.properties.set("diagram.sloppiness", sloppiness)

    @action(name="pref.reset-tool-after-create", state=False)
    def reset_tool_after_create(self, active: bool):
        self.properties.set("reset-tool-after-create", active)
