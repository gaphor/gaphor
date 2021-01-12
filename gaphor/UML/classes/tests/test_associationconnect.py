import pytest

from gaphor import UML
from gaphor.diagram.tests.fixtures import allow, connect, disconnect, get_connected
from gaphor.UML.classes.association import AssociationItem
from gaphor.UML.classes.klass import ClassItem


@pytest.fixture
def connected_association(create):
    asc = create(AssociationItem)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)

    connect(asc, asc.head, c1)
    assert asc.subject is None  # no UML metaclass yet

    connect(asc, asc.tail, c2)
    assert asc.subject is not None

    return asc, c1, c2


@pytest.fixture
def clone(create):
    def _clone(item):
        new = create(type(item))
        new.subject = item.subject
        new.head_subject = item.head_subject
        new.tail_subject = item.tail_subject
        return new

    return _clone


def test_glue_to_class(connected_association):
    asc, c1, c2 = connected_association

    glued = allow(asc, asc.head, c1)
    assert glued

    connect(asc, asc.head, c1)

    glued = allow(asc, asc.tail, c2)
    assert glued


def test_association_item_connect(connected_association, element_factory):
    asc, c1, c2 = connected_association

    # Diagram, Class *2, Property *2, Association
    assert len(element_factory.lselect()) == 6
    assert asc.head_subject is not None
    assert asc.tail_subject is not None


def test_association_item_reconnect(connected_association, create):
    asc, c1, c2 = connected_association
    c3 = create(ClassItem, UML.Class)

    UML.model.set_navigability(asc.subject, asc.tail_subject, True)

    a = asc.subject

    connect(asc, asc.tail, c3)

    assert a is asc.subject
    ends = [p.type for p in asc.subject.memberEnd]
    assert c1.subject in ends
    assert c3.subject in ends
    assert c2.subject not in ends
    assert asc.tail_subject.navigability is True


def test_disconnect_should_disconnect_model(connected_association):
    asc, c1, c2 = connected_association

    disconnect(asc, asc.head)
    disconnect(asc, asc.tail)
    assert c1 is not get_connected(asc, asc.head)
    assert c2 is not get_connected(asc, asc.tail)

    assert asc.subject
    assert len(asc.subject.memberEnd) == 2
    assert asc.subject.memberEnd[0].type is None
    assert asc.subject.memberEnd[1].type is None


def test_disconnect_of_second_association_should_leave_model_in_tact(
    connected_association, clone
):
    asc, c1, c2 = connected_association
    new = clone(asc)

    disconnect(new, new.head)
    assert asc.subject.memberEnd[0].type is c1.subject
    assert asc.subject.memberEnd[1].type is c2.subject
    assert new.subject is asc.subject


def test_disconnect_of_navigable_end_should_remove_owner_relationship(
    connected_association,
):
    asc, c1, c2 = connected_association

    UML.model.set_navigability(asc.subject, asc.head_subject, True)

    assert asc.head_subject in c2.subject.ownedAttribute

    disconnect(asc, asc.head)

    assert asc.subject
    assert len(asc.subject.memberEnd) == 2
    assert asc.subject.memberEnd[0].type is None
    assert asc.head_subject not in c2.subject.ownedAttribute
    assert asc.tail_subject not in c1.subject.ownedAttribute
    assert asc.head_subject.type is None
    assert asc.tail_subject.type is None


def test_allow_reconnect_for_single_presentation(connected_association, create):
    asc, c1, c2 = connected_association
    c3 = create(ClassItem, UML.Class)

    assert allow(asc, asc.head, c3)


def test_allow_reconnect_on_same_class_for_multiple_presentations(
    connected_association, clone, create
):
    asc, c1, c2 = connected_association
    new = clone(asc)

    assert allow(new, new.head, c1)
    assert allow(new, new.tail, c2)


def test_allow_reconnect_if_only_one_connected_presentations(
    connected_association, clone, create
):
    asc, c1, c2 = connected_association
    clone(asc)

    c3 = create(ClassItem, UML.Class)

    assert allow(asc, asc.head, c3)


def test_disallow_connect_if_already_connected_with_presentations(
    connected_association, clone, create
):
    asc, c1, c2 = connected_association
    new = clone(asc)

    c3 = create(ClassItem, UML.Class)

    assert not allow(new, new.head, c3)


def test_disallow_reconnect_if_multiple_connected_presentations(
    connected_association, clone, create
):
    asc, c1, c2 = connected_association
    new = clone(asc)
    connect(new, new.head, c1)

    c3 = create(ClassItem, UML.Class)

    assert not allow(asc, asc.head, c3)


def test_allow_both_ends_connected_to_the_same_class(create, clone):
    asc = create(AssociationItem)
    c1 = create(ClassItem, UML.Class)
    connect(asc, asc.head, c1)
    connect(asc, asc.tail, c1)

    new = clone(asc)
    c2 = create(ClassItem, UML.Class)
    assert allow(new, new.head, c1)
    assert allow(new, new.tail, c1)
    assert not allow(new, new.head, c2)
    assert not allow(new, new.tail, c2)
