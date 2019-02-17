"""
Test the UndoManager.
"""

from gaphor.tests.testcase import TestCase
from gaphor.services.undomanager import UndoManager
from gaphor.transaction import Transaction
from gaphor.application import Application


class TestUndoManager(TestCase):
    def test_transactions(self):

        undo_manager = UndoManager()
        undo_manager.init(None)

        assert not undo_manager._current_transaction

        # undo_manager.begin_transaction()
        tx = Transaction()

        # assert undo_manager._transaction_depth == 1
        assert undo_manager._current_transaction

        current = undo_manager._current_transaction
        # undo_manager.begin_transaction()
        tx2 = Transaction()
        # assert undo_manager._transaction_depth == 2
        # assert undo_manager._transaction_depth == 1
        assert undo_manager._current_transaction is current

        # undo_manager.commit_transaction()
        tx2.commit()

        # assert undo_manager._transaction_depth == 1
        assert undo_manager._current_transaction is current

        # undo_manager.commit_transaction()
        tx.commit()
        # assert undo_manager._transaction_depth == 0
        assert undo_manager._current_transaction is None

        undo_manager.shutdown()

    def test_not_in_transaction(self):
        undo_manager = UndoManager()
        undo_manager.init(Application)

        action = object()
        undo_manager.add_undo_action(action)
        assert undo_manager._current_transaction is None

        undo_manager.begin_transaction()
        undo_manager.add_undo_action(action)
        assert undo_manager._current_transaction
        assert undo_manager.can_undo()
        assert len(undo_manager._current_transaction._actions) == 1

        undo_manager.shutdown()

    def test_actions(self):
        undone = [0]

        def undo_action(undone=undone):
            # print 'undo_action called'
            undone[0] = 1
            undo_manager.add_undo_action(redo_action)

        def redo_action(undone=undone):
            # print 'redo_action called'
            undone[0] = -1
            undo_manager.add_undo_action(undo_action)

        undo_manager = UndoManager()
        undo_manager.init(Application)

        # undo_manager.begin_transaction()
        tx = Transaction()
        undo_manager.add_undo_action(undo_action)
        assert undo_manager._current_transaction
        assert undo_manager.can_undo()
        assert len(undo_manager._current_transaction._actions) == 1

        # undo_manager.commit_transaction()
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

        undo_manager.shutdown()

    def test_undo_attribute(self):
        import types
        from gaphor.UML.properties import attribute
        from gaphor.UML.element import Element

        undo_manager = UndoManager()
        undo_manager.init(Application)

        class A(Element):
            attr = attribute("attr", bytes, default="default")

        a = A()
        assert a.attr == "default", a.attr
        undo_manager.begin_transaction()
        a.attr = "five"

        undo_manager.commit_transaction()
        assert a.attr == "five"

        undo_manager.undo_transaction()
        assert a.attr == "default", a.attr

        undo_manager.redo_transaction()
        assert a.attr == "five"

        undo_manager.shutdown()

    def test_undo_association_1_x(self):
        from gaphor.UML.properties import association
        from gaphor.UML.element import Element

        undo_manager = UndoManager()
        undo_manager.init(Application)

        class A(Element):
            pass

        class B(Element):
            pass

        A.one = association("one", B, 0, 1, opposite="two")
        B.two = association("two", A, 0, 1)

        a = A()
        b = B()

        assert a.one is None
        assert b.two is None

        undo_manager.begin_transaction()
        a.one = b

        undo_manager.commit_transaction()
        assert a.one is b
        assert b.two is a
        assert len(undo_manager._undo_stack) == 1
        assert len(undo_manager._undo_stack[0]._actions) == 2, undo_manager._undo_stack[
            0
        ]._actions

        undo_manager.undo_transaction()
        assert a.one is None
        assert b.two is None
        assert undo_manager.can_redo()
        assert len(undo_manager._redo_stack) == 1
        assert len(undo_manager._redo_stack[0]._actions) == 2, undo_manager._redo_stack[
            0
        ]._actions

        undo_manager.redo_transaction()
        assert len(undo_manager._undo_stack) == 1
        assert len(undo_manager._undo_stack[0]._actions) == 2, undo_manager._undo_stack[
            0
        ]._actions
        assert b.two is a
        assert a.one is b

        undo_manager.shutdown()

    def test_undo_association_1_n(self):
        from gaphor.UML.properties import association
        from gaphor.UML.element import Element

        undo_manager = UndoManager()
        undo_manager.init(Application)

        class A(Element):
            pass

        class B(Element):
            pass

        A.one = association("one", B, lower=0, upper=1, opposite="two")
        B.two = association("two", A, lower=0, upper="*", opposite="one")

        a1 = A()
        a2 = A()
        b1 = B()
        b2 = B()

        undo_manager.begin_transaction()
        b1.two = a1

        undo_manager.commit_transaction()
        assert a1 in b1.two
        assert b1 is a1.one
        assert len(undo_manager._undo_stack) == 1
        assert len(undo_manager._undo_stack[0]._actions) == 2, undo_manager._undo_stack[
            0
        ]._actions

        undo_manager.undo_transaction()
        assert len(b1.two) == 0
        assert a1.one is None
        assert undo_manager.can_redo()
        assert len(undo_manager._redo_stack) == 1
        assert len(undo_manager._redo_stack[0]._actions) == 2, undo_manager._redo_stack[
            0
        ]._actions

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

        undo_manager.shutdown()

    def test_element_factory_undo(self):
        from gaphor.UML.element import Element

        ef = self.element_factory
        ef.flush()

        undo_manager = UndoManager()
        undo_manager.init(Application)
        undo_manager.begin_transaction()
        p = ef.create(Element)

        assert undo_manager._current_transaction
        assert undo_manager._current_transaction._actions
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

        undo_manager.shutdown()

    def test_element_factory_rollback(self):
        from gaphor.UML.element import Element

        ef = self.element_factory
        ef.flush()
        undo_manager = UndoManager()
        undo_manager.init(Application)
        undo_manager.begin_transaction()
        p = ef.create(Element)

        assert undo_manager._current_transaction
        assert undo_manager._current_transaction._actions
        assert undo_manager.can_undo()

        undo_manager.rollback_transaction()
        assert not undo_manager.can_undo()
        assert ef.size() == 0

        undo_manager.shutdown()

    def test_uml_associations(self):

        from zope import component
        from gaphor.UML.interfaces import IAssociationChangeEvent
        from gaphor.UML.properties import association, derivedunion
        from gaphor.UML import Element

        class A(Element):
            is_unlinked = False

            def unlink(self):
                self.is_unlinked = True
                Element.unlink(self)

        A.a1 = association("a1", A, upper=1)
        A.a2 = association("a2", A, upper=1)
        A.b1 = association("b1", A, upper="*")
        A.b2 = association("b2", A, upper="*")
        A.b3 = association("b3", A, upper=1)

        A.derived_a = derivedunion("derived_a", 0, 1, A.a1, A.a2)
        A.derived_b = derivedunion("derived_b", 0, "*", A.b1, A.b2, A.b3)

        events = []

        @component.adapter(IAssociationChangeEvent)
        def handler(event, events=events):
            events.append(event)

        compreg = Application.get_service("component_registry")
        compreg.register_handler(handler)
        try:
            a = A()

            undo_manager = UndoManager()
            undo_manager.init(Application)
            undo_manager.begin_transaction()

            a.a1 = A()
            undo_manager.commit_transaction()

            assert len(events) == 1, events
            assert events[0].property is A.a1
            assert undo_manager.can_undo()

            undo_manager.undo_transaction()
            assert not undo_manager.can_undo()
            assert undo_manager.can_redo()
            assert len(events) == 2, events
            assert events[1].property is A.a1

        finally:
            compreg.unregister_handler(handler)
            undo_manager.shutdown()

    def test_redo_stack(self):
        from gaphor.UML.element import Element

        undo_manager = UndoManager()
        undo_manager.init(Application)
        undo_manager.begin_transaction()
        ef = self.element_factory
        ef.flush()

        p = ef.create(Element)

        assert undo_manager._current_transaction
        assert undo_manager._current_transaction._actions
        assert undo_manager.can_undo()

        undo_manager.commit_transaction()
        assert undo_manager.can_undo()
        assert ef.size() == 1, ef.size()

        with Transaction():
            q = ef.create(Element)

        assert undo_manager.can_undo()
        assert not undo_manager.can_redo()
        assert ef.size() == 2

        undo_manager.undo_transaction()
        assert undo_manager.can_undo()
        self.assertEqual(1, len(undo_manager._undo_stack))
        self.assertEqual(1, len(undo_manager._redo_stack))
        assert undo_manager.can_redo()
        assert ef.size() == 1

        undo_manager.undo_transaction()
        assert not undo_manager.can_undo()
        assert undo_manager.can_redo()
        self.assertEqual(0, len(undo_manager._undo_stack))
        self.assertEqual(2, len(undo_manager._redo_stack))
        # assert ef.size() == 0

        undo_manager.redo_transaction()
        self.assertEqual(1, len(undo_manager._undo_stack))
        self.assertEqual(1, len(undo_manager._redo_stack))
        assert undo_manager.can_undo()
        assert undo_manager.can_redo()
        assert ef.size() == 1

        undo_manager.redo_transaction()
        assert undo_manager.can_undo()
        assert not undo_manager.can_redo()
        assert ef.size() == 2

        assert p in ef.lselect()

        undo_manager.shutdown()
