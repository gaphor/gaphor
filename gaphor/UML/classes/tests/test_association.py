"""Unit tests for AssociationItem."""

import pytest

from gaphor import UML
from gaphor.diagram.tests.fixtures import connect, get_connected
from gaphor.UML.classes.association import (
    AssociationItem,
    draw_default_head,
    draw_head_navigable,
    draw_head_none,
)
from gaphor.UML.classes.klass import ClassItem


class Items:
    def __init__(self, assoc, class1, class2):
        self.assoc = assoc
        self.class1 = class1
        self.class2 = class2


@pytest.fixture
def items(create):
    return Items(
        create(AssociationItem),
        create(ClassItem, UML.Class),
        create(ClassItem, UML.Class),
    )


def test_create(items):
    """Test association creation and its basic properties."""
    connect(items.assoc, items.assoc.head, items.class1)
    connect(items.assoc, items.assoc.tail, items.class2)

    assert isinstance(items.assoc.subject, UML.Association)
    assert items.assoc.head_subject is not None
    assert items.assoc.tail_subject is not None

    assert not items.assoc.show_direction

    items.assoc.show_direction = True
    assert items.assoc.show_direction


def test_direction(items):
    """Test association direction inverting."""
    connect(items.assoc, items.assoc.head, items.class1)
    connect(items.assoc, items.assoc.tail, items.class2)

    assert items.assoc.head_subject is items.assoc.subject.memberEnd[0]
    assert items.assoc.tail_subject is items.assoc.subject.memberEnd[1]


def test_invert_direction(items):
    connect(items.assoc, items.assoc.head, items.class1)
    connect(items.assoc, items.assoc.tail, items.class2)

    items.assoc.invert_direction()

    assert items.assoc.subject.memberEnd
    assert items.assoc.head_subject is items.assoc.subject.memberEnd[1]
    assert items.assoc.tail_subject is items.assoc.subject.memberEnd[0]


def test_association_end_updates(create, diagram):
    """Test association end navigability connected to a class."""
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)
    a = create(AssociationItem)

    connect(a, a.head, c1)
    c = get_connected(a, a.head)
    assert c is c1

    connect(a, a.tail, c2)
    c = get_connected(a, a.tail)
    assert c is c2

    assert a.subject.memberEnd, a.subject.memberEnd

    assert a.subject.memberEnd[0] is a.head_subject
    assert a.subject.memberEnd[1] is a.tail_subject
    assert a.subject.memberEnd[0].name is None

    a.subject.memberEnd[0].name = "blah"
    diagram.update({a})

    assert a.head_end.name == "+ blah", a.head_end.name


def test_association_end_owner_handles(items):
    assert items.assoc.head_end.owner_handle is items.assoc.head
    assert items.assoc.tail_end.owner_handle is items.assoc.tail


@pytest.mark.parametrize(
    "navigability,draw_func",
    [[None, draw_default_head], [True, draw_head_navigable], [False, draw_head_none]],
)
def test_association_head_end_not_navigable(items, navigability, draw_func):
    connect(items.assoc, items.assoc.head, items.class1)
    connect(items.assoc, items.assoc.tail, items.class2)

    end = items.assoc.head_end
    UML.recipes.set_navigability(end.subject.association, end.subject, navigability)
    items.assoc.update()

    assert items.assoc.head_subject.navigability is navigability
    assert items.assoc.draw_head is draw_func
