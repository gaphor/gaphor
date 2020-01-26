import pytest

from gaphor import UML
from gaphor.application import Session, distribution
from gaphor.storage.storage import load


@pytest.fixture
def session():
    session = Session()
    yield session
    session.shutdown()


@pytest.fixture
def element_factory(session):
    element_factory = session.get_service("element_factory")
    path = distribution().locate_file("test-diagrams/issue_53.gaphor")
    load(path, element_factory)
    yield element_factory
    element_factory.shutdown()


def test_package_removal(session, element_factory):
    # Find all profile instances
    profiles = element_factory.lselect(lambda e: e.isKindOf(UML.Profile))

    # Check there is 1 profile
    assert len(profiles) == 1

    # Check the profile has 1 presentation
    assert len(profiles[0].presentation) == 1

    # Unlink the presentation
    profiles[0].presentation[0].unlink()

    assert not element_factory.lselect(lambda e: e.isKindOf(UML.Profile))

    classes = element_factory.lselect(lambda e: e.isKindOf(UML.Class))
    assert len(classes) == 1

    # Check if the link is really removed:
    assert not classes[0].appliedStereotype
    assert not element_factory.lselect(lambda e: e.isKindOf(UML.InstanceSpecification))
    assert len(element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))) == 3


def test_package_removal_by_removing_the_diagram(element_factory):

    diagram = element_factory.lselect(
        lambda e: e.isKindOf(UML.Diagram) and e.name == "Stereotypes diagram"
    )[0]

    assert diagram

    diagram.unlink()

    assert not element_factory.lselect(lambda e: e.isKindOf(UML.Profile))

    classes = element_factory.lselect(lambda e: e.isKindOf(UML.Class))
    assert len(classes) == 1

    # Check if the link is really removed:
    assert not classes[0].appliedStereotype
    assert not element_factory.lselect(lambda e: e.isKindOf(UML.InstanceSpecification))
    assert len(element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))) == 2
