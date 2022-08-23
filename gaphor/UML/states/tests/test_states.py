from gaphor import UML
from gaphor.core.modeling import Diagram
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
