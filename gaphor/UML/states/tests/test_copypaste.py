from gaphor import UML
from gaphor.diagram.tests.fixtures import connect, copy_clear_and_paste_link
from gaphor.UML.states import StateItem, TransitionItem


def test_state_with_behaviors(diagram, element_factory):
    state: UML.State = element_factory.create(UML.State)
    state.entry = element_factory.create(UML.Behavior)
    state.entry.name = "hi"
    state.exit = element_factory.create(UML.Behavior)
    state.exit.name = "bye"
    state.doActivity = element_factory.create(UML.Behavior)
    state.doActivity.name = "act"

    state_item = diagram.create(StateItem, subject=state)

    new_items = copy_clear_and_paste_link({state_item}, diagram, element_factory)
    new_state_item = new_items.pop()

    assert isinstance(new_state_item, StateItem)
    assert new_state_item.subject.entry.name == "hi"
    assert new_state_item.subject.exit.name == "bye"
    assert new_state_item.subject.doActivity.name == "act"


def test_connected_transition(diagram, element_factory):
    state_item_1 = diagram.create(StateItem, subject=element_factory.create(UML.State))
    state_item_2 = diagram.create(StateItem, subject=element_factory.create(UML.State))
    transition_item = diagram.create(TransitionItem)

    connect(transition_item, transition_item.head, state_item_1)
    connect(transition_item, transition_item.tail, state_item_2)
    transition_item.subject.guard.specification = "[test]"

    new_items = copy_clear_and_paste_link({transition_item}, diagram, element_factory)
    new_transition_item = new_items.pop()

    assert isinstance(new_transition_item, TransitionItem), new_items
    assert new_transition_item.subject.guard
    assert new_transition_item.subject.guard.specification == "[test]"
