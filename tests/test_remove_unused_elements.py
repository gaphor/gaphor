import pytest

from gaphor import UML
from gaphor.application import Session
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML import diagramitems


@pytest.fixture
def session():
    session = Session()

    yield session
    session.shutdown()


@pytest.fixture
def event_manager(session):
    return session.get_service("event_manager")


@pytest.fixture
def element_factory(session):
    return session.get_service("element_factory")


@pytest.fixture
def properties(session):
    return session.get_service("properties")


@pytest.fixture
def diagram(event_manager, element_factory):
    with Transaction(event_manager):
        return element_factory.create(Diagram)


@pytest.fixture
def classes_and_association(diagram, event_manager, element_factory):
    with Transaction(event_manager):
        c1 = diagram.create(
            diagramitems.ClassItem, subject=element_factory.create(UML.Class)
        )
        c2 = diagram.create(
            diagramitems.ClassItem, subject=element_factory.create(UML.Class)
        )

        a = diagram.create(diagramitems.AssociationItem)
        connect(a, a.handles()[0], c1)
        connect(a, a.handles()[1], c2)

    return c1.subject, c2.subject, a.subject


@pytest.mark.parametrize(
    ["remove_unused_elements", "comparator"],
    [
        [True, lambda a: not a],
        [False, lambda a: a],
    ],
)
def test_delete_diagram(
    classes_and_association,
    diagram,
    event_manager,
    element_factory,
    properties,
    remove_unused_elements,
    comparator,
):
    properties.set("remove-unused-elements", remove_unused_elements)

    c1, c2, a = classes_and_association

    with Transaction(event_manager):
        diagram.unlink()

    assert comparator(c1 in element_factory)
    assert comparator(c2 in element_factory)
    assert comparator(a in element_factory)
