import pytest

from gaphor import UML
from gaphor.diagram.diagramtoolbox import tooliter
from gaphor.UML.toolbox import uml_toolbox_actions

state_node_names = [
    "state",
    "final-state",
    "initial-pseudostate",
    "shallow-history-pseudostate",
    "deep-history-pseudostate",
    "join-pseudostate",
    "fork-pseudostate",
    "junction-pseudostate",
    "choice-pseudostate",
    "entry-point-pseudostate",
    "exit-point-pseudostate",
    "terminate-pseudostate",
]


@pytest.fixture
def item_factory(request):
    return next(
        t for t in tooliter(uml_toolbox_actions) if t.id == f"toolbox-{request.param}"
    ).item_factory


@pytest.mark.parametrize("item_factory", state_node_names, indirect=True)
def test_create_state_on_diagram_should_create_a_state_machine_with_region(
    diagram, item_factory
):
    state = item_factory(diagram)

    assert state.subject.container
    assert state.subject.container.stateMachine


@pytest.mark.parametrize("item_factory", state_node_names, indirect=True)
def test_create_state_should_add_to_existing_state_machine(
    diagram, item_factory, element_factory
):
    state_machine = element_factory.create(UML.StateMachine)
    state = item_factory(diagram)
    region = state.subject.container

    assert region
    assert region.stateMachine is state_machine


@pytest.mark.parametrize("item_factory", state_node_names, indirect=True)
def test_create_state_should_add_to_existing_state_machine_and_region(
    diagram, item_factory, element_factory
):
    state_machine = element_factory.create(UML.StateMachine)
    region = element_factory.create(UML.Region)
    region.stateMachine = state_machine

    state = item_factory(diagram)

    assert state.subject.container is region


@pytest.mark.parametrize("item_factory", state_node_names, indirect=True)
def test_create_state_should_add_to_existing_state_machine_and_region_in_package(
    diagram, item_factory, element_factory
):
    state_machine = element_factory.create(UML.StateMachine)
    region = element_factory.create(UML.Region)
    region.stateMachine = state_machine

    package = element_factory.create(UML.Package)
    diagram.element = package
    state_machine.package = package

    state = item_factory(diagram)

    assert state.subject.container is region


@pytest.mark.parametrize("item_factory", state_node_names, indirect=True)
def test_create_state_should_add_to_existing_state_machine_in_package(
    diagram, item_factory, element_factory
):
    state_machine = element_factory.create(UML.StateMachine)

    package = element_factory.create(UML.Package)
    diagram.element = package
    state_machine.package = package

    state = item_factory(diagram)

    assert state.subject.container.stateMachine is state_machine
