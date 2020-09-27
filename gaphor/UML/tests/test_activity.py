import pytest

from gaphor import UML
from gaphor.ui.diagrampage import tooliter
from gaphor.UML.toolbox import uml_toolbox_actions


@pytest.fixture
def action_factory():
    return next(
        t for t in tooliter(uml_toolbox_actions) if t.id == "toolbox-action"
    ).item_factory


def test_create_action_should_create_an_activity(diagram, action_factory):
    action = action_factory(diagram)

    assert action.subject.activity
    assert action.subject.owner is action.subject.activity


def test_create_action_should_add_to_existing_activity(
    diagram, action_factory, element_factory
):
    activity = element_factory.create(UML.Activity)
    action = action_factory(diagram)

    assert action.subject.activity is activity


def test_create_action_should_add_to_existing_activity_in_package(
    diagram, action_factory, element_factory
):
    package = element_factory.create(UML.Package)
    diagram.package = package
    activity = element_factory.create(UML.Activity)
    activity.package = package
    action = action_factory(diagram)

    assert action.subject.activity is activity
