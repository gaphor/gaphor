"""Unit tests for AssociationItem."""

import pytest

from gaphor import UML
from gaphor.UML.classes.association import (
    AssociationItem,
    draw_default_head,
    draw_head_navigable,
    draw_head_none,
)
from gaphor.UML.classes.klass import ClassItem


@pytest.fixture
def case(case):
    case.assoc = case.create(AssociationItem)
    case.class1 = case.create(ClassItem, UML.Class)
    case.class2 = case.create(ClassItem, UML.Class)
    return case


def test_create(case):
    """Test association creation and its basic properties."""
    case.connect(case.assoc, case.assoc.head, case.class1)
    case.connect(case.assoc, case.assoc.tail, case.class2)

    assert isinstance(case.assoc.subject, UML.Association)
    assert case.assoc.head_subject is not None
    assert case.assoc.tail_subject is not None

    assert not case.assoc.show_direction

    case.assoc.show_direction = True
    assert case.assoc.show_direction


def test_direction(case):
    """Test association direction inverting."""
    case.connect(case.assoc, case.assoc.head, case.class1)
    case.connect(case.assoc, case.assoc.tail, case.class2)

    assert case.assoc.head_subject is case.assoc.subject.memberEnd[0]
    assert case.assoc.tail_subject is case.assoc.subject.memberEnd[1]


def test_invert_direction(case):
    case.connect(case.assoc, case.assoc.head, case.class1)
    case.connect(case.assoc, case.assoc.tail, case.class2)

    case.assoc.invert_direction()

    assert case.assoc.subject.memberEnd
    assert case.assoc.head_subject is case.assoc.subject.memberEnd[1]
    assert case.assoc.tail_subject is case.assoc.subject.memberEnd[0]


def test_association_end_updates(case):
    """Test association end navigability connected to a class."""
    c1 = case.create(ClassItem, UML.Class)
    c2 = case.create(ClassItem, UML.Class)
    a = case.create(AssociationItem)

    case.connect(a, a.head, c1)
    c = case.get_connected(a.head)
    assert c is c1

    case.connect(a, a.tail, c2)
    c = case.get_connected(a.tail)
    assert c is c2

    assert a.subject.memberEnd, a.subject.memberEnd

    assert a.subject.memberEnd[0] is a.head_subject
    assert a.subject.memberEnd[1] is a.tail_subject
    assert a.subject.memberEnd[0].name is None

    a.subject.memberEnd[0].name = "blah"
    case.diagram.update_now((a,))

    assert a.head_end._name == "+ blah", a.head_end.get_name()


def test_association_orthogonal(case):
    c1 = case.create(ClassItem, UML.Class)
    c2 = case.create(ClassItem, UML.Class)
    a = case.create(AssociationItem)

    case.connect(a, a.head, c1)
    c = case.get_connected(a.head)
    assert c is c1

    a.matrix.translate(100, 100)
    case.connect(a, a.tail, c2)
    c = case.get_connected(a.tail)
    assert c is c2

    with pytest.raises(ValueError):
        a.orthogonal = True


def test_association_end_owner_handles(case):
    assert case.assoc.head_end.owner_handle is case.assoc.head
    assert case.assoc.tail_end.owner_handle is case.assoc.tail


@pytest.mark.parametrize(
    "navigability,draw_func",
    [[None, draw_default_head], [True, draw_head_navigable], [False, draw_head_none]],
)
def test_association_head_end_not_navigable(case, navigability, draw_func):
    case.connect(case.assoc, case.assoc.head, case.class1)
    case.connect(case.assoc, case.assoc.tail, case.class2)

    end = case.assoc.head_end
    UML.recipes.set_navigability(end.subject.association, end.subject, navigability)
    case.assoc.update_ends()

    assert case.assoc.head_subject.navigability is navigability
    assert case.assoc.draw_head is draw_func
