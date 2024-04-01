from gaphor.diagram.drop import drop, grow_parent
from gaphor.diagram.group import group, ungroup
from gaphor.UML.states.pseudostates import PseudostateItem
from gaphor.UML.states.state import StateItem
from gaphor.UML.states.statemachine import StateMachineItem
from gaphor.UML.states.transition import TransitionItem


@drop.register(StateItem, StateItem)
@drop.register(StateItem, StateMachineItem)
@drop.register(PseudostateItem, StateItem)
@drop.register(PseudostateItem, StateMachineItem)
@drop.register(TransitionItem, StateItem)
@drop.register(TransitionItem, StateMachineItem)
def drop_region(item, new_parent: StateItem | StateMachineItem, x, y):
    assert item.diagram is new_parent.diagram

    if not item.subject:
        return

    old_parent = item.parent
    target_subject = new_parent.region_at_point((x, y))

    if target_subject is item.subject.container:
        return

    if old_parent and ungroup(old_parent.subject, item.subject):
        item.change_parent(None)
        old_parent.request_update()

    if group(target_subject, item.subject):
        grow_parent(new_parent, item)
        item.change_parent(new_parent)
