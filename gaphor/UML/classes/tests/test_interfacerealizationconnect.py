import pytest

from gaphor import UML
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML.classes.interface import InterfaceItem
from gaphor.UML.classes.interfacerealization import InterfaceRealizationItem
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


def test_interface_realization_multiple_connection(create, other_create):
    c1 = create(InterfaceItem, UML.Interface)
    c2 = create(ClassItem, UML.Class)
    rel1 = create(InterfaceRealizationItem)

    connect(rel1, rel1.head, c1)
    connect(rel1, rel1.tail, c2)

    c3 = other_create(InterfaceItem)
    c3.subject = c1.subject
    c4 = other_create(ClassItem)
    c4.subject = c2.subject
    rel2 = other_create(InterfaceRealizationItem)

    connect(rel2, rel2.head, c3)
    connect(rel2, rel2.tail, c4)

    assert rel1.subject is rel2.subject
