"""
Test the UndoManager.
"""

import unittest
from gaphor.undomanager import UndoManager

class TestUndoManager(unittest.TestCase):

    def test_1(self):
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

    def test_2(self):
        undo_manager = UndoManager()

        action = object()
        undo_manager.add_undo_action(action)
        assert undo_manager._current_transaction is None

        undo_manager.begin_transaction()
        undo_manager.add_undo_action(action)
        assert undo_manager._current_transaction
        assert len(undo_manager._current_transaction._actions) == 1

# vim:sw=4:et
