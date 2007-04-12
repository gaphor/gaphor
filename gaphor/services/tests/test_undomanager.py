"""
Test the UndoManager.
"""

import unittest
from gaphor.services.undomanager import UndoManager
from gaphor.transaction import Transaction


class TestUndoManager(unittest.TestCase):

    def test_transactions(self):

        undo_manager = UndoManager()
        undo_manager.init(None)

        assert undo_manager._transaction_depth == 0
        assert not undo_manager._current_transaction

        #undo_manager.begin_transaction()
        tx = Transaction()

        assert undo_manager._transaction_depth == 1
        assert undo_manager._current_transaction

        current = undo_manager._current_transaction
        #undo_manager.begin_transaction()
        tx2 = Transaction()
        #assert undo_manager._transaction_depth == 2
        assert undo_manager._transaction_depth == 1
        assert undo_manager._current_transaction is current

        #undo_manager.commit_transaction()
        tx2.commit()

        assert undo_manager._transaction_depth == 1
        assert undo_manager._current_transaction is current

        #undo_manager.commit_transaction()
        tx.commit()
        assert undo_manager._transaction_depth == 0
        assert undo_manager._current_transaction is None

    def test_not_in_transaction(self):
        undo_manager = UndoManager()
        undo_manager.init(None)

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
            #print 'undo_action called'
            undone[0] = 1
            undo_manager.add_undo_action(redo_action)

        def redo_action(undone=undone):
            #print 'redo_action called'
            undone[0] = -1
            undo_manager.add_undo_action(undo_action)

        undo_manager = UndoManager()
        undo_manager.init(None)

        #undo_manager.begin_transaction()
        tx = Transaction()
        undo_manager.add_undo_action(undo_action)
        assert undo_manager._current_transaction
        assert undo_manager.can_undo()
        assert len(undo_manager._current_transaction._actions) == 1

        #undo_manager.commit_transaction()
        tx.commit()

        undo_manager.undo_transaction()
        assert not undo_manager.can_undo(), undo_manager._undo_stack
        assert undone[0] == 1, undone
        
        undone[0] = 0

        assert undo_manager.can_redo(), undo_manager._redo_stack

        undo_manager.redo_transaction()
        assert not undo_manager.can_redo()
        assert undo_manager.can_undo()
        assert undone[0] == -1, undone

    def test_undo_attribute(self):
        import types
        from gaphor.UML.properties import attribute
        from gaphor.UML.element import Element
        undo_manager = UndoManager()
        undo_manager.init(None)

        class A(Element):
            attr = attribute('attr', types.StringType, default='default')

        a = A()
        assert a.attr == 'default', a.attr
        undo_manager.begin_transaction()
        a.attr = 'five'

        undo_manager.commit_transaction()
        assert a.attr == 'five'

        undo_manager.undo_transaction()
        assert a.attr == 'default', a.attr

        undo_manager.redo_transaction()
        assert a.attr == 'five'

    def test_undo_aassociation_1_x(self):
        from gaphor.UML.properties import association
        from gaphor.UML.element import Element
        undo_manager = UndoManager()
        undo_manager.init(None)

        class A(Element): pass
        class B(Element): pass

        A.one = association('one', B, 0, 1, opposite='two')
        B.two = association('two', A, 0, 1)

        a = A()
        b = B()

        assert a.one is None
        assert b.two is None

        undo_manager.begin_transaction()
        a.one = b

        undo_manager.commit_transaction()
        assert a.one is b
        assert b.two is a

        undo_manager.undo_transaction()
        assert a.one is None
        assert b.two is None

        undo_manager.redo_transaction()
        assert a.one is b
        assert b.two is a

    def test_undo_association_1_n(self):
        from gaphor.UML.properties import association
        from gaphor.UML.element import Element
        undo_manager = UndoManager()
        undo_manager.init(None)
 
        class A(Element): pass
        class B(Element): pass

        A.one = association('one', B, lower=0, upper=1, opposite='two')
        B.two = association('two', A, lower=0, upper='*', opposite='one')

        a1 = A()
        a2 = A()
        b1 = B()
        b2 = B()


        undo_manager.begin_transaction()
        b1.two = a1
        
        undo_manager.commit_transaction()
        assert a1 in b1.two
        assert b1 is a1.one

        undo_manager.undo_transaction()
        assert len(b1.two) == 0
        assert a1.one is None

        undo_manager.redo_transaction()
        assert a1 in b1.two
        assert b1 is a1.one

        undo_manager.begin_transaction()
        b1.two = a2

        undo_manager.commit_transaction()
        assert a1 in b1.two
        assert a2 in b1.two
        assert b1 is a1.one
        assert b1 is a2.one

    def test_element_factory_undo(self):
        from gaphor.UML.elementfactory import ElementFactory
        from gaphor.UML.element import Element
        undo_manager = UndoManager()
        undo_manager.init(None)
        undo_manager.begin_transaction()
        ef = ElementFactory()
        p = ef.create(Element)

        assert undo_manager.can_undo()

        undo_manager.commit_transaction()
        assert undo_manager.can_undo()
        assert ef.size() == 1

        undo_manager.undo_transaction()
        assert not undo_manager.can_undo()
        assert undo_manager.can_redo()
        assert ef.size() == 0

        undo_manager.redo_transaction()
        assert undo_manager.can_undo()
        assert not undo_manager.can_redo()
        assert ef.size() == 1
        assert ef.lselect()[0] is p
        
# vim:sw=4:et
