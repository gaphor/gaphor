"""
Test the UndoManager.
"""

import unittest
from gaphor.undomanager import UndoManager

class TestUndoManager(unittest.TestCase):

    def test_transactions(self):

        undo_manager = UndoManager()
        assert undo_manager._transaction_depth == 0
        assert not undo_manager._current_transaction

        undo_manager.begin_transaction()
        assert undo_manager._transaction_depth == 1
        assert undo_manager._current_transaction

        current = undo_manager._current_transaction
        undo_manager.begin_transaction()
        assert undo_manager._transaction_depth == 2
        assert undo_manager._current_transaction is current

        undo_manager.commit_transaction()
        assert undo_manager._transaction_depth == 1
        assert undo_manager._current_transaction is current

        undo_manager.commit_transaction()
        assert undo_manager._transaction_depth == 0
        assert undo_manager._current_transaction is None

    def test_not_in_transaction(self):
        undo_manager = UndoManager()

        action = object()
        undo_manager.add_undo_action(action)
        assert undo_manager._current_transaction is None

        undo_manager.begin_transaction()
        undo_manager.add_undo_action(action)
        assert undo_manager._current_transaction
        assert undo_manager.can_undo()
        assert len(undo_manager._current_transaction._actions) == 1

        
    def test_actions(self):
        undone = [ 0 ]
        def undo_action(undone=undone):
            assert undo_manager._in_undo
            undone[0] = 1
            return undo_action

        undo_manager = UndoManager()

        undo_manager.begin_transaction()
        undo_manager.add_undo_action(undo_action)
        assert undo_manager._current_transaction
        assert undo_manager.can_undo()
        assert len(undo_manager._current_transaction._actions) == 1

        undo_manager.commit_transaction()

        undo_manager.undo_transaction()
        assert not undo_manager.can_undo()
        assert undone[0] == 1
        
        undone[0] = 0

        assert undo_manager.can_redo()

        undo_manager.redo_transaction()
        assert not undo_manager.can_redo()
        assert undo_manager.can_undo()
        assert undone[0] == 1
# vim:sw=4:et
