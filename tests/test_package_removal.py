import pytest

from gaphor import UML
from gaphor.application import Session
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram
from gaphor.storage.storage import load


@pytest.fixture
def session():
    session = Session()
    yield session
    session.shutdown()


@pytest.fixture
def event_manager(session):
    return session.get_service("event_manager")


@pytest.fixture
def element_factory(session, test_models):
    element_factory = session.get_service("element_factory")
    modeling_language = session.get_service("modeling_language")
    with (test_models / "issue_53.gaphor").open(encoding="utf-8") as f:
        load(f, element_factory, modeling_language)
    yield element_factory
    element_factory.shutdown()


def test_package_removal(event_manager, element_factory):
    # Find all profile instances
    profiles = element_factory.lselect(UML.Profile)

    # Check there is 1 profile
    assert len(profiles) == 1

    # Check the profile has 1 presentation
    assert len(profiles[0].presentation) == 1

    # Unlink the presentation and profile
    with Transaction(event_manager):
        profiles[0].presentation[0].unlink()
        profiles[0].unlink()

    assert not element_factory.lselect(UML.Profile)

    classes = element_factory.lselect(UML.Class)
    assert len(classes) == 1

    # Check if the link is really removed:
    assert not classes[0].appliedStereotype
    assert not element_factory.lselect(UML.InstanceSpecification)
    assert len(element_factory.lselect(Diagram)) == 3


def test_package_removal_by_removing_the_diagram(event_manager, element_factory):
    diagram = element_factory.lselect(
        lambda e: e.isKindOf(Diagram) and e.name == "Stereotypes diagram"
    )[0]

    assert diagram

    with Transaction(event_manager):
        diagram.unlink()

    assert not element_factory.lselect(UML.Profile)

    classes = element_factory.lselect(UML.Class)
    assert len(classes) == 1

    # Check if the link is really removed:
    assert not classes[0].appliedStereotype
    assert not element_factory.lselect(UML.InstanceSpecification)
    assert len(element_factory.lselect(Diagram)) == 2
