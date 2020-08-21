import pytest

from gaphor import UML
from gaphor.diagram.tests.fixtures import allow, connect, disconnect
from gaphor.UML.classes.association import AssociationItem
from gaphor.UML.classes.klass import ClassItem


@pytest.fixture
def create(diagram, element_factory):
    def _create(item_class, element_class=None):
        return diagram.create(
            item_class,
            subject=(element_factory.create(element_class) if element_class else None),
        )

    return _create


def get_connected(item, handle):
    """
    Get item connected to a handle.
    """
    cinfo = item.canvas.get_connection(handle)
    if cinfo:
        return cinfo.connected  # type: ignore[no-any-return] # noqa: F723
    return None


def test_glue_to_class(create):
    asc = create(AssociationItem)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)

    glued = allow(asc, asc.head, c1)
    assert glued

    connect(asc, asc.head, c1)

    glued = allow(asc, asc.tail, c2)
    assert glued


def test_association_item_connect(create, element_factory):
    asc = create(AssociationItem)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)

    connect(asc, asc.head, c1)
    assert asc.subject is None  # no UML metaclass yet

    connect(asc, asc.tail, c2)
    assert asc.subject is not None

    # Diagram, Class *2, Property *2, Association, StyleSheet
    assert len(element_factory.lselect()) == 7
    assert asc.head_end.subject is not None
    assert asc.tail_end.subject is not None


def test_association_item_reconnect(create):
    asc = create(AssociationItem)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)
    c3 = create(ClassItem, UML.Class)

    connect(asc, asc.head, c1)
    connect(asc, asc.tail, c2)
    UML.model.set_navigability(asc.subject, asc.tail_end.subject, True)

    a = asc.subject

    connect(asc, asc.tail, c3)

    assert a is asc.subject
    ends = [p.type for p in asc.subject.memberEnd]
    assert c1.subject in ends
    assert c3.subject in ends
    assert c2.subject not in ends
    assert asc.tail_end.subject.navigability


def test_disconnect(create):
    """Test association item disconnection
    """
    asc = create(AssociationItem)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)

    connect(asc, asc.head, c1)
    assert asc.subject is None  # no UML metaclass yet

    connect(asc, asc.tail, c2)
    assert asc.subject is not None

    disconnect(asc, asc.head)
    disconnect(asc, asc.tail)
    assert c1 is not get_connected(asc, asc.head)
    assert c2 is not get_connected(asc, asc.tail)
