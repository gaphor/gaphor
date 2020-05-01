from gaphor import UML
from gaphor.diagram.tests.fixtures import clear_model, connect, copy_clear_and_paste
from gaphor.UML.states import StateItem


def test_state_with_behaviors(diagram, element_factory):
    state: UML.State = element_factory.create(UML.State)
    state.entry = element_factory.create(UML.Behavior)
    state.entry.name = "hi"
    state.exit = element_factory.create(UML.Behavior)
    state.exit.name = "bye"
    state.doActivity = element_factory.create(UML.Behavior)
    state.doActivity.name = "act"

    state_item = diagram.create(StateItem, subject=state)

    new_items = copy_clear_and_paste({state_item}, diagram, element_factory)
    new_state_item = new_items.pop()

    assert isinstance(new_state_item, StateItem)
    assert new_state_item.subject.entry.name == "hi"
    assert new_state_item.subject.exit.name == "bye"
    assert new_state_item.subject.doActivity.name == "act"
