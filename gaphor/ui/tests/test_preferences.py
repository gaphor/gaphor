from gi.repository import Gtk

from gaphor.ui.preferences import Preferences


class MainWindowMock:
    def __init__(self):
        self.window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)


def test_preferences_window():
    prefs = Preferences(MainWindowMock(), {})

    dialog = prefs.open()
    action_group = dialog.get_action_group("pref")

    assert (
        action_group.lookup_action("reset-tool-after-create").get_state().get_boolean()
        is True
    )
