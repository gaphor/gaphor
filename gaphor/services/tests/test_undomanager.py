"""
Test the UndoManager.
"""

from gaphor.core import event_handler
from gaphor.tests.testcase import TestCase
from gaphor.services.undomanager import UndoManager
from gaphor.services.eventmanager import EventManager
from gaphor.UML.elementfactory import ElementFactory
from gaphor.transaction import Transaction


class TestUndoManager(TestCase):
    def test_transactions(self):

        event_manager = EventManager()
        undo_manager = UndoManager(event_manager)

        assert not undo_manager._current_transaction

        # undo_manager.begin_transaction()
        tx = Transaction(event_manager)

        # assert undo_manager._transaction_depth == 1
        assert undo_manager._current_transaction

        current = undo_manager._current_transaction
        # undo_manager.begin_transaction()
        tx2 = Transaction(event_manager)
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
        event_manager = EventManager()
        undo_manager = UndoManager(event_manager)

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

        event_manager = EventManager()
        undo_manager = UndoManager(event_manager)

        # undo_manager.begin_transaction()
        tx = Transaction(event_manager)
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
        from gaphor.UML.properties import attribute
        from gaphor.UML.element import Element

        event_manager = EventManager()
        undo_manager = UndoManager(event_manager)
        element_factory = ElementFactory(event_manager)

        class A(Element):
            attr = attribute("attr", bytes, default="default")

        a = element_factory.create(A)
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

        event_manager = EventManager()
        undo_manager = UndoManager(event_manager)
        element_factory = ElementFactory(event_manager)

        class A(Element):
            pass

        class B(Element):
            pass

        A.one = association("one", B, 0, 1, opposite="two")
        B.two = association("two", A, 0, 1)

        a = element_factory.create(A)
        b = element_factory.create(B)

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

        event_manager = EventManager()
        undo_manager = UndoManager(event_manager)
        element_factory = ElementFactory(event_manager)

        class A(Element):
            pass

        class B(Element):
            pass

        A.one = association("one", B, lower=0, upper=1, opposite="two")
        B.two = association("two", A, lower=0, upper="*", opposite="one")

        a1 = element_factory.create(A)
        a2 = element_factory.create(A)
        b1 = element_factory.create(B)
        b2 = element_factory.create(B)

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

        event_manager = EventManager()
        undo_manager = UndoManager(event_manager)
        element_factory = ElementFactory(event_manager)

        undo_manager.begin_transaction()
        p = element_factory.create(Element)

        assert undo_manager._current_transaction
        assert undo_manager._current_transaction._actions
        assert undo_manager.can_undo()

        undo_manager.commit_transaction()
        assert undo_manager.can_undo()
        assert element_factory.size() == 1

        undo_manager.undo_transaction()
        assert not undo_manager.can_undo()
        assert undo_manager.can_redo()
        assert element_factory.size() == 0

        undo_manager.redo_transaction()
        assert undo_manager.can_undo()
        assert not undo_manager.can_redo()
        assert element_factory.size() == 1
        assert element_factory.lselect()[0] is p

        undo_manager.shutdown()

    def test_element_factory_rollback(self):
        from gaphor.UML.element import Element

        event_manager = EventManager()
        undo_manager = UndoManager(event_manager)
        element_factory = ElementFactory(event_manager)

        undo_manager.begin_transaction()
        p = element_factory.create(Element)

        assert undo_manager._current_transaction
        assert undo_manager._current_transaction._actions
        assert undo_manager.can_undo()

        undo_manager.rollback_transaction()
        assert not undo_manager.can_undo()
        assert element_factory.size() == 0

        undo_manager.shutdown()

    def test_uml_associations(self):

        from gaphor.UML.event import AssociationUpdated
        from gaphor.UML.properties import association, derivedunion
        from gaphor.UML import Element

        event_manager = EventManager()
        undo_manager = UndoManager(event_manager)
        element_factory = ElementFactory(event_manager)

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

        @event_handler(AssociationUpdated)
        def handler(event, events=events):
            events.append(event)

        event_manager.subscribe(handler)
        try:
            a = element_factory.create(A)

            undo_manager.begin_transaction()

            a.a1 = element_factory.create(A)
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
            event_manager.unsubscribe(handler)
            undo_manager.shutdown()

    def test_redo_stack(self):
        from gaphor.UML.element import Element

        event_manager = EventManager()
        undo_manager = UndoManager(event_manager)
        element_factory = ElementFactory(event_manager)

        undo_manager.begin_transaction()

        p = element_factory.create(Element)

        assert undo_manager._current_transaction
        assert undo_manager._current_transaction._actions
        assert undo_manager.can_undo()

        undo_manager.commit_transaction()
        assert undo_manager.can_undo()
        assert element_factory.size() == 1, element_factory.size()

        with Transaction(event_manager):
            q = element_factory.create(Element)

        assert undo_manager.can_undo()
        assert not undo_manager.can_redo()
        assert element_factory.size() == 2

        undo_manager.undo_transaction()
        assert undo_manager.can_undo()
        assert 1 == len(undo_manager._undo_stack)
        assert 1 == len(undo_manager._redo_stack)
        assert undo_manager.can_redo()
        assert element_factory.size() == 1

        undo_manager.undo_transaction()
        assert not undo_manager.can_undo()
        assert undo_manager.can_redo()
        assert 0 == len(undo_manager._undo_stack)
        assert 2 == len(undo_manager._redo_stack)
        # assert element_factory.size() == 0

        undo_manager.redo_transaction()
        assert 1 == len(undo_manager._undo_stack)
        assert 1 == len(undo_manager._redo_stack)
        assert undo_manager.can_undo()
        assert undo_manager.can_redo()
        assert element_factory.size() == 1

        undo_manager.redo_transaction()
        assert undo_manager.can_undo()
        assert not undo_manager.can_redo()
        assert element_factory.size() == 2

        assert p in element_factory.lselect()

        undo_manager.shutdown()
