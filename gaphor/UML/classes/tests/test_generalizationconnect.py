import pytest

from gaphor import UML
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram
from gaphor.diagram.tests.fixtures import allow, connect, get_connected
from gaphor.UML.classes.generalization import GeneralizationItem
from gaphor.UML.classes.klass import ClassItem


@pytest.fixture
def other_diagram(element_factory, event_manager) -> Diagram:
    with Transaction(event_manager):
        diagram = element_factory.create(Diagram)
    yield diagram
    with Transaction(event_manager):
        diagram.unlink()


@pytest.fixture
def other_create(other_diagram, element_factory):
    def _create(item_class, element_class=None):
        return other_diagram.create(
            item_class,
            subject=(element_factory.create(element_class) if element_class else None),
        )

    return _create


def test_generalization_multiple_connection(create, other_create):
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)
    gen1 = create(GeneralizationItem)

    connect(gen1, gen1.tail, c1)
    connect(gen1, gen1.head, c2)

    c3 = other_create(ClassItem)
    c3.subject = c1.subject
    c4 = other_create(ClassItem)
    c4.subject = c2.subject
    gen2 = other_create(GeneralizationItem)

    connect(gen2, gen2.tail, c3)
    connect(gen2, gen2.head, c4)

    assert gen1.subject is gen2.subject


def test_generalization_glue(create):
    gen = create(GeneralizationItem)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)

    glued = allow(gen, gen.tail, c1)
    assert glued

    connect(gen, gen.tail, c1)
    assert get_connected(gen, gen.tail) is c1
    assert gen.subject is None

    glued = allow(gen, gen.head, c2)
    assert glued


def test_generalization_connection(create):
    gen = create(GeneralizationItem)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)

    connect(gen, gen.tail, c1)
    assert get_connected(gen, gen.tail) is c1

    connect(gen, gen.head, c2)
    assert gen.subject is not None
    assert gen.subject.general is c1.subject
    assert gen.subject.specific is c2.subject


def test_generalization_reconnection(create, element_factory):
    gen = create(GeneralizationItem)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)

    connect(gen, gen.tail, c1)
    assert get_connected(gen, gen.tail) is c1

    connect(gen, gen.head, c2)
    assert gen.subject is not None
    assert gen.subject.general is c1.subject
    assert gen.subject.specific is c2.subject

    # Now do the same on a new diagram:
    diagram2 = element_factory.create(Diagram)
    c3 = diagram2.create(ClassItem, subject=c1.subject)
    c4 = diagram2.create(ClassItem, subject=c2.subject)
    gen2 = diagram2.create(GeneralizationItem)

    connect(gen2, gen2.head, c3)
    cinfo = diagram2.connections.get_connection(gen2.head)
    assert cinfo is not None
    assert cinfo.connected is c3

    connect(gen2, gen2.tail, c4)
    assert gen.subject is not gen2.subject
    assert len(c2.subject.generalization) == 1
    assert c2.subject.generalization[0] is gen.subject


def test_generalization_reconnection2(create):
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)
    c3 = create(ClassItem, UML.Class)
    gen = create(GeneralizationItem)

    # connect: c1 -> c2
    connect(gen, gen.head, c1)
    connect(gen, gen.tail, c2)

    s = gen.subject

    # reconnect: c2 -> c3
    connect(gen, gen.tail, c3)

    assert s is gen.subject
    assert c1.subject is gen.subject.specific
    assert c3.subject is gen.subject.general
    assert c2.subject is not gen.subject.general
