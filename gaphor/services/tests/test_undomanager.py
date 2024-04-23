# ruff: noqa: SLF001

import pytest

from gaphor.core import event_handler
from gaphor.core.modeling import Element
from gaphor.core.modeling.event import AssociationUpdated
from gaphor.core.modeling.properties import association, attribute, derivedunion
from gaphor.services.undomanager import NotInTransactionException
from gaphor.tests.raises import raises_exception_group
from gaphor.transaction import Transaction


def test_nested_transactions(event_manager, undo_manager):
    assert not undo_manager._current_transaction

    tx = Transaction(event_manager)

    assert undo_manager._current_transaction

    current = undo_manager._current_transaction
    tx2 = Transaction(event_manager)
    assert undo_manager._current_transaction is current

    tx2.commit()

    assert undo_manager._current_transaction is current

    tx.commit()
    assert undo_manager._current_transaction is None


def test_not_in_transaction(undo_manager):
    def action():
        pass

    with pytest.raises(NotInTransactionException):
        undo_manager.add_undo_action(action)

    undo_manager.begin_transaction()
    undo_manager.add_undo_action(action)
    assert undo_manager._current_transaction
    assert undo_manager.can_undo()
    assert len(undo_manager._current_transaction._actions) == 1


def test_actions(event_manager, undo_manager):
    undone = [0]

    def undo_action(undone=undone):
        undone[0] = 1
        undo_manager.add_undo_action(redo_action)

    def redo_action(undone=undone):
        undone[0] = -1
        undo_manager.add_undo_action(undo_action)

    tx = Transaction(event_manager)
    undo_manager.add_undo_action(undo_action)
    assert undo_manager._current_transaction
    assert undo_manager.can_undo()
    assert len(undo_manager._current_transaction._actions) == 1

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


def test_undo_attribute(element_factory, undo_manager):
    class A(Element):
        attr = attribute("attr", bytes, default="default")

    undo_manager.begin_transaction()
    a = element_factory.create(A)
    undo_manager.commit_transaction()

    assert a.attr == "default", a.attr

    undo_manager.begin_transaction()
    a.attr = "five"
    undo_manager.commit_transaction()

    assert a.attr == "five"

    undo_manager.undo_transaction()

    assert a.attr == "default", a.attr

    undo_manager.redo_transaction()

    assert a.attr == "five"


def test_no_value_change_if_not_in_transaction(
    event_manager, element_factory, undo_manager
):
    class A(Element):
        attr = attribute("attr", bytes, default="default")

    with Transaction(event_manager):
        a = element_factory.create(A)

    with raises_exception_group(NotInTransactionException):
        a.attr = "foo"

    assert a.attr == "default"


def test_undo_association_1_x(event_manager, element_factory, undo_manager):
    class A(Element):
        pass

    class B(Element):
        pass

    A.one = association("one", B, 0, 1, opposite="two")
    B.two = association("two", A, 0, 1)

    with Transaction(event_manager):
        a = element_factory.create(A)
        b = element_factory.create(B)
    undo_manager.clear_undo_stack()

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
    assert len(undo_manager._redo_stack[0]._actions) == 3, undo_manager._redo_stack[
        0
    ]._actions

    undo_manager.redo_transaction()
    assert len(undo_manager._undo_stack) == 1
    assert len(undo_manager._undo_stack[0]._actions) == 2, undo_manager._undo_stack[
        0
    ]._actions
    assert b.two is a
    assert a.one is b


def test_undo_association_1_n(event_manager, element_factory, undo_manager):
    class A(Element):
        pass

    class B(Element):
        pass

    A.one = association("one", B, upper=1, opposite="two")
    B.two = association("two", A, upper="*", opposite="one")

    with Transaction(event_manager):
        a1 = element_factory.create(A)
        a2 = element_factory.create(A)
        b1 = element_factory.create(B)
        element_factory.create(B)

    undo_manager.clear_undo_stack()

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


def test_undo_association_undo_in_same_order(
    event_manager, element_factory, undo_manager
):
    class A(Element):
        pass

    class B(Element):
        pass

    A.one = association("one", B, upper=1, opposite="two")
    B.two = association("two", A, upper="*", opposite="one")

    with Transaction(event_manager):
        a1 = element_factory.create(A)
        a2 = element_factory.create(A)
        a3 = element_factory.create(A)
        b = element_factory.create(B)
        b.two = a1
        b.two = a2
        b.two = a3

    with Transaction(event_manager):
        del b.two[a2]

    undo_manager.undo_transaction()

    assert [e.id for e in b.two] == [a1.id, a2.id, a3.id]


def test_element_factory_undo(element_factory, undo_manager):
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
    assert element_factory.lookup(p.id)


def test_element_factory_rollback(element_factory, undo_manager):
    undo_manager.begin_transaction()
    element_factory.create(Element)

    assert undo_manager._current_transaction
    assert undo_manager._current_transaction._actions
    assert undo_manager.can_undo()

    undo_manager.rollback_transaction()
    assert not undo_manager.can_undo()
    assert element_factory.size() == 0


def test_uml_associations(event_manager, element_factory, undo_manager):
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

    A.derived_a = derivedunion("derived_a", A, 0, 1, A.a1, A.a2)
    A.derived_b = derivedunion("derived_b", A, 0, "*", A.b1, A.b2, A.b3)

    events = []

    @event_handler(AssociationUpdated)
    def handler(event, events=events):
        events.append(event)

    event_manager.subscribe(handler)

    undo_manager.begin_transaction()

    a = element_factory.create(A)
    a.a1 = element_factory.create(A)
    undo_manager.commit_transaction()

    assert len(events) == 2, events  # both  AssociationSet and DerivedSet events
    assert events[0].property is A.a1
    assert undo_manager.can_undo()

    undo_manager.undo_transaction()
    assert not undo_manager.can_undo()
    assert undo_manager.can_redo()
    assert len(events) == 4, events
    assert events[2].property is A.a1


def test_set_association_outside_transaction(
    undo_manager, element_factory, event_manager
):
    class A(Element):
        pass

    A.a = association("a", A, upper=1, opposite="b")
    A.b = association("b", A, opposite="a")

    with Transaction(event_manager):
        a = element_factory.create(A)
        b = element_factory.create(A)

    with raises_exception_group(NotInTransactionException):
        a.a = b

    assert not a.b
    assert a.a is None


def test_set_multi_association_outside_transaction(
    undo_manager, element_factory, event_manager
):
    class A(Element):
        pass

    A.a = association("a", A, upper=1, opposite="b")
    A.b = association("b", A, opposite="a")

    with Transaction(event_manager):
        a = element_factory.create(A)
        b = element_factory.create(A)

    with raises_exception_group(NotInTransactionException):
        a.b = b

    assert not a.b
    assert a.a is None


def test_update_association_outside_transaction(
    undo_manager, element_factory, event_manager
):
    class A(Element):
        pass

    A.a = association("a", A, upper=1, opposite="b")
    A.b = association("b", A, opposite="a")

    with Transaction(event_manager):
        a = element_factory.create(A)
        b = element_factory.create(A)
        a.a = b
        other = element_factory.create(A)

    with raises_exception_group(NotInTransactionException):
        a.a = other

    assert a in b.b
    assert a.a is b


def test_set_derived_union_outside_transaction(
    undo_manager, element_factory, event_manager
):
    class A(Element):
        pass

    A.a = association("a", A, upper=1, opposite="b")
    A.b = association("b", A, opposite="a")
    A.derived_a = derivedunion("derived_a", A, 0, 1, A.a)
    A.derived_b = derivedunion("derived_b", A, 0, "*", A.b)

    with Transaction(event_manager):
        a = element_factory.create(A)
        b = element_factory.create(A)

    with raises_exception_group(NotInTransactionException):
        a.a = b

    with raises_exception_group(NotInTransactionException):
        a.b = b

    assert not a.b
    assert not a.a
    assert not a.derived_a
    assert not a.derived_b


def test_rollback_transaction(undo_manager, element_factory, event_manager):
    class A(Element):
        pass

    with Transaction(event_manager) as tx:
        element_factory.create(A)
        tx.rollback()

    assert not undo_manager.can_undo()


def test_redo_stack(event_manager, element_factory, undo_manager):
    undo_manager.begin_transaction()

    p = element_factory.create(Element)

    assert undo_manager._current_transaction
    assert undo_manager._current_transaction._actions
    assert undo_manager.can_undo()

    undo_manager.commit_transaction()
    assert undo_manager.can_undo()
    assert element_factory.size() == 1, element_factory.size()

    with Transaction(event_manager):
        element_factory.create(Element)

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

    assert element_factory.lookup(p.id)
