"""GUI Undo/redo actions

Undo and redo are special, since they share their
action name with text widget undo actions.

This service makes sure the text edit undo/redo actions
have preference over window level undo.

Undo/redo have to use the same action names, so
the functions are accessible from the (macOS)
menu bar.
"""

from gaphor.abc import ActionProvider, Service
from gaphor.action import action
from gaphor.services.undomanager import UndoManager
from gaphor.ui.mainwindow import MainWindow


class UndoActions(Service, ActionProvider):
    def __init__(self, undo_manager: UndoManager, main_window: MainWindow):
        self.undo_manager = undo_manager
        self.main_window = main_window
        self.in_action = False

    def shutdown(self):
        pass

    @action(name="text.undo", shortcut="<Primary>z")
    def undo_transaction(self):
        self.activate_on_focused_widget("text.undo", self.undo_manager.undo_transaction)

    @action(name="text.redo", shortcut="<Primary><Shift>z")
    def redo_transaction(self):
        self.activate_on_focused_widget("text.redo", self.undo_manager.redo_transaction)

    def activate_on_focused_widget(self, action_name, func):
        if self.in_action:
            return func()

        self.in_action = True
        try:
            if not (
                (win := self.main_window.window)
                and (widget := win.get_focus())
                and widget.activate_action(action_name)
            ):
                func()
        finally:
            self.in_action = False
