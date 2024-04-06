from gaphor import UML
from gaphor.core.modeling import Diagram, StyleSheet
from gaphor.UML.states.state import StateItem
from gaphor.UML.states.statemachine import StateMachineItem


def test_state(create):
    assert create(StateItem, UML.State)


def test_statemachine(create):
    assert create(StateMachineItem, UML.StateMachine)


def test_activities_persistence(create, element_factory, saver, loader):
    """Test state activities saving/loading."""
    # all activities
    s1 = create(StateItem, UML.State)
    s1.subject.name = "s1"
    s1.subject.entry = s1.model.create(UML.Activity)
    s1.subject.exit = s1.model.create(UML.Activity)
    s1.subject.doActivity = s1.model.create(UML.Activity)
    s1.subject.entry.name = "test 1 entry"
    s1.subject.exit.name = "test 1 exit"
    s1.subject.doActivity.name = "test 1 do"

    data = saver()
    loader(data)
    diagram = next(element_factory.select(Diagram))

    s1 = next(diagram.select(StateItem))
    assert "test 1 entry" == s1.subject.entry.name
    assert "test 1 exit" == s1.subject.exit.name
    assert "test 1 do" == s1.subject.doActivity.name


def test_state_machine_with_regions(create, diagram, element_factory):
    element_factory.create(StyleSheet)
    state_machine: StateMachineItem = create(StateMachineItem, UML.StateMachine)
    state_machine.subject.region = element_factory.create(UML.Region)
    state_machine.subject.region = element_factory.create(UML.Region)

    diagram.update()

    assert (
        state_machine.region_at_point((10, state_machine.height / 2))
        is state_machine.subject.region[0]
    )
    assert (
        state_machine.region_at_point((10, state_machine.height - 10))
        is state_machine.subject.region[1]
    )


def test_state_with_regions(create, diagram, element_factory):
    element_factory.create(StyleSheet)
    state: StateItem = create(StateItem, UML.State)
    state.subject.region = element_factory.create(UML.Region)
    state.subject.region = element_factory.create(UML.Region)

    diagram.update()

    assert state.region_at_point((10, state.height / 2)) is state.subject.region[0]
    assert state.region_at_point((10, state.height - 10)) is state.subject.region[1]
