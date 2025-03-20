import pytest
from gi.repository import Gtk

from gaphor.services.undomanager import UndoManager
from gaphor.ui.undoactions import UndoActions


class MockMainWindow:
    def __init__(self):
        self.window = Gtk.Window()


@pytest.fixture
def main_window():
    return MockMainWindow()


@pytest.fixture
def undo_manager(event_manager, element_factory):
    undo_manager = UndoManager(event_manager, element_factory)
    yield undo_manager
    undo_manager.shutdown()


@pytest.fixture
def undo_actions(undo_manager, main_window):
    return UndoActions(undo_manager, main_window)


@pytest.mark.parametrize(
    "focus,action", [[True, "undo"], [True, "redo"], [False, "undo"], [False, "redo"]]
)
def test_undo_action(undo_actions, main_window, monkeypatch, focus, action):
    activated_action = None
    undo_manager_called = False

    gtk_text_activate_action = Gtk.Text.activate_action

    def mock_activate_action(self, name):
        nonlocal activated_action
        activated_action = name
        return gtk_text_activate_action(self, name)

    def mock_undo_transaction(self):
        nonlocal undo_manager_called
        undo_manager_called = True

    monkeypatch.setattr(Gtk.Text, "activate_action", mock_activate_action)
    monkeypatch.setattr(UndoManager, f"{action}_transaction", mock_undo_transaction)

    win = main_window.window
    entry = Gtk.Entry.new()
    win.set_child(entry)
    win.present()
    win.set_focus(entry if focus else None)

    getattr(undo_actions, f"{action}_transaction")()

    if focus:
        assert activated_action == f"text.{action}"
        assert not undo_manager_called
    else:
        assert not activated_action
        assert undo_manager_called
