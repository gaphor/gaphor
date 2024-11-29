import pytest

from gaphor import UML
from gaphor.core.modeling import Diagram
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
    asc, _c1, _c2 = connected_association

    # Diagram, Class *2, Property *2, Association
    assert len(element_factory.lselect()) == 9
    assert asc.head_subject is not None
    assert asc.tail_subject is not None


def test_association_item_reconnect_copies_properties(connected_association, create):
    asc, c1, c2 = connected_association
    c3 = create(ClassItem, UML.Class)

    asc.subject.name = "Name"

    a = asc.subject

    connect(asc, asc.tail, c3)

    assert a is not asc.subject
    ends = [p.type for p in asc.subject.memberEnd]
    assert c1.subject in ends
    assert c3.subject in ends
    assert c2.subject not in ends
    assert asc.subject.name == "Name"


def test_association_item_reconnect_with_navigability(connected_association, create):
    asc, _c1, _c2 = connected_association
    c3 = create(ClassItem, UML.Class)

    UML.recipes.set_navigability(asc.subject, asc.tail_subject, True)
    connect(asc, asc.tail, c3)

    assert asc.tail_subject.navigability is True


def test_association_item_reconnect_with_aggregation(connected_association, create):
    asc, _c1, _c2 = connected_association
    c3 = create(ClassItem, UML.Class)

    asc.tail_subject.aggregation = "composite"
    connect(asc, asc.tail, c3)

    assert asc.tail_subject.aggregation == "composite"


def test_disconnect_should_disconnect_model(
    connected_association, element_factory, sanitizer_service
):
    asc, c1, c2 = connected_association

    disconnect(asc, asc.head)
    disconnect(asc, asc.tail)
    assert c1 is not get_connected(asc, asc.head)
    assert c2 is not get_connected(asc, asc.tail)

    assert not asc.subject
    assert not asc.head_subject
    assert not asc.tail_subject
    assert not element_factory.lselect(UML.Property)


def test_disconnect_of_second_association_should_leave_model_in_tact(
    connected_association, clone, sanitizer_service
):
    asc, c1, c2 = connected_association
    new = clone(asc)

    disconnect(new, new.head)
    assert asc.subject.memberEnd[0].type is c1.subject
    assert asc.subject.memberEnd[1].type is c2.subject
    assert new.subject is asc.subject


def test_disconnect_of_navigable_end_should_remove_owner_relationship(
    connected_association, element_factory, sanitizer_service
):
    asc, _c1, c2 = connected_association

    UML.recipes.set_navigability(asc.subject, asc.head_subject, True)

    assert asc.head_subject in c2.subject.ownedAttribute

    disconnect(asc, asc.head)

    assert not asc.subject
    assert not asc.head_subject
    assert not asc.tail_subject
    assert not element_factory.lselect(UML.Property)


def test_allow_reconnect_for_single_presentation(connected_association, create):
    asc, _c1, _c2 = connected_association
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
    asc, _c1, _c2 = connected_association
    clone(asc)

    c3 = create(ClassItem, UML.Class)

    assert allow(asc, asc.head, c3)


def test_create_association_in_new_diagram_should_reuse_existing(
    connected_association, element_factory
):
    asc, c1, c2 = connected_association

    diagram2 = element_factory.create(Diagram)
    c3 = diagram2.create(ClassItem, subject=c1.subject)
    c4 = diagram2.create(ClassItem, subject=c2.subject)
    asc2 = diagram2.create(AssociationItem)

    connect(asc2, asc2.head, c3)
    connect(asc2, asc2.tail, c4)

    assert asc.subject is asc2.subject
    assert asc.head_subject is asc2.head_subject
    assert asc.tail_subject is asc2.tail_subject


def test_create_association_in_new_diagram_reversed_should_reuse_existing(
    connected_association, element_factory
):
    asc, c1, c2 = connected_association

    diagram2 = element_factory.create(Diagram)
    c3 = diagram2.create(ClassItem, subject=c1.subject)
    c4 = diagram2.create(ClassItem, subject=c2.subject)
    asc2 = diagram2.create(AssociationItem)

    connect(asc2, asc2.tail, c3)
    connect(asc2, asc2.head, c4)

    assert asc.subject is asc2.subject
    assert asc.head_subject is asc2.tail_subject
    assert asc.tail_subject is asc2.head_subject


def test_disconnect_association_in_new_diagram_should_clear_ends(
    connected_association, element_factory
):
    asc, c1, c2 = connected_association

    diagram2 = element_factory.create(Diagram)
    c3 = diagram2.create(ClassItem, subject=c1.subject)
    c4 = diagram2.create(ClassItem, subject=c2.subject)
    asc2 = diagram2.create(AssociationItem)

    connect(asc2, asc2.tail, c3)
    connect(asc2, asc2.head, c4)
    disconnect(asc, asc.head)

    assert not asc.subject
    assert not asc.head_subject
    assert not asc.tail_subject


@pytest.mark.xfail
def test_connect_association_missing_head_subject(create, element_factory):
    asc_item = create(AssociationItem, UML.Association)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)

    asc = asc_item.subject = UML.recipes.create_association(c1.subject, c2.subject)

    # Now break the association by removing one end:
    asc.memberEnd[0].unlink()

    connect(asc_item, asc_item.tail, c1)
    connect(asc_item, asc_item.head, c2)

    assert len(asc_item.subject.memberEnd) == 2
    assert not asc_item.head_subject
    assert asc_item.tail_subject
