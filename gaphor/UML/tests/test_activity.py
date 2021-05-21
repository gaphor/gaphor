import pytest

from gaphor import UML
from gaphor.diagram.diagramtoolbox import tooliter
from gaphor.UML.toolbox import uml_toolbox_actions

activity_node_names = [
    "action",
    "initial-node",
    "activity-final-node",
    "flow-final-node",
    "decision-node",
    "fork-node",
    "object-node",
    "send-signal-action",
    "accept-event-action",
]


@pytest.fixture
def item_factory(request):
    return next(
        t for t in tooliter(uml_toolbox_actions) if t.id == f"toolbox-{request.param}"
    ).item_factory


@pytest.mark.parametrize("item_factory", activity_node_names, indirect=True)
def test_create_action_should_create_an_activity(diagram, item_factory):
    action = item_factory(diagram)

    assert action.subject.activity
    assert action.subject.owner is action.subject.activity


@pytest.mark.parametrize("item_factory", activity_node_names, indirect=True)
def test_create_action_should_add_to_existing_activity(
    diagram, item_factory, element_factory
):
    activity = element_factory.create(UML.Activity)
    action = item_factory(diagram)

    assert action.subject.activity is activity


@pytest.mark.parametrize("item_factory", activity_node_names, indirect=True)
def test_create_action_should_add_to_existing_activity_in_package(
    diagram, item_factory, element_factory
):
    package = element_factory.create(UML.Package)
    diagram.element = package
    activity = element_factory.create(UML.Activity)
    activity.package = package
    action = item_factory(diagram)

    assert action.subject.activity is activity
