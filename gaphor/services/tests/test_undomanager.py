"""
Test the UndoManager.
"""

import unittest
from gaphor.undomanager import UndoManager, undoableproperty

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


    def test_undoableproperty(self):
        class A(object):
            def _set_x(self, value):
                self._x = value
            def _del_x(self):
                del self._x
            x = undoableproperty(lambda s: s._x, _set_x, _del_x)

        a = A()
        assert A.x

        a.x = 3
        assert a.x == 3
        assert a._x == 3

        a.x = 9
        assert a.x == 9
        assert a._x == 9

        del a.x
        assert not hasattr(a, 'x')
        assert not hasattr(a, '_x')

        a.x = 3
        assert hasattr(a, 'x')
        assert hasattr(a, '_x')
        
    def test_undoableproperty_property(self):
        undo_manager = UndoManager()
        class A(object):
            def _set_x(self, value):
                self._x = value
            def _del_x(self):
                del self._x
            x = undoableproperty(property=property(lambda s: s._x, _set_x, _del_x),
                                 undo_manager=undo_manager)

        a = A()
        a.x = 3
        assert a.x == 3

    def test_undoableproperty_in_transaction(self):
        undo_manager = UndoManager()
        class A(object):
            def _set_x(self, value):
                self._x = value
            def _del_x(self):
                del self._x
            x = undoableproperty(lambda s: s._x, _set_x, _del_x,
                                 undo_manager=undo_manager)

        a = A()
        a.x = 3
        undo_manager.begin_transaction()
        assert undo_manager._current_transaction
        a.x = 2

        undo_manager.commit_transaction()
        assert undo_manager._undo_stack
        assert a.x == 2

        undo_manager.undo_transaction()
        assert not undo_manager._undo_stack
        assert undo_manager._redo_stack
        assert a.x == 3

        undo_manager.redo_transaction()
        assert undo_manager._undo_stack
        assert not undo_manager._redo_stack
        
        assert a.x == 2

# vim:sw=4:et
