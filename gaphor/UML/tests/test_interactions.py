import pytest

from gaphor import UML
from gaphor.diagram.diagramtoolbox import tooliter
from gaphor.UML.interactions.interaction import InteractionItem
from gaphor.UML.toolbox import uml_toolbox_actions


@pytest.fixture
def interaction(diagram, element_factory):
    return diagram.create(
        InteractionItem, subject=element_factory.create(UML.Interaction)
    )


@pytest.fixture
def lifeline_factory():
    return next(
        t for t in tooliter(uml_toolbox_actions) if t.id == "toolbox-lifeline"
    ).item_factory


def test_create_lifeline_on_diagram_should_create_an_interaction(
    diagram, lifeline_factory
):
    lifeline = lifeline_factory(diagram)

    assert lifeline.subject.interaction


def test_create_lifeline_on_diagram_should_use_existing_interaction(
    diagram, lifeline_factory, element_factory
):
    interaction = element_factory.create(UML.Interaction)
    lifeline = lifeline_factory(diagram)

    assert lifeline.subject.interaction is interaction


def test_create_lifeline_on_diagram_in_package_should_create_an_interaction(
    diagram, element_factory, lifeline_factory
):
    package = element_factory.create(UML.Package)
    diagram.element = package
    lifeline = lifeline_factory(diagram)

    assert lifeline.subject.interaction
    assert lifeline.subject.interaction.package is package


def test_create_lifeline_over_interaction_uses_that_interaction(
    diagram, interaction, lifeline_factory
):
    lifeline = lifeline_factory(diagram, parent=interaction)

    assert lifeline.subject.interaction is interaction.subject
