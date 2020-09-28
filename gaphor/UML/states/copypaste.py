from typing import NamedTuple, Optional

from gaphor.diagram.copypaste import (
    ElementCopy,
    copy,
    copy_element,
    paste,
    paste_element,
)
from gaphor.UML import State, Transition


class StateCopy(NamedTuple):
    state: ElementCopy
    entry: Optional[ElementCopy]
    exit: Optional[ElementCopy]
    do_activity: Optional[ElementCopy]


@copy.register
def copy_state(element: State):
    return StateCopy(
        state=copy_element(element),
        entry=copy_element(element.entry) if element.entry else None,
        exit=copy_element(element.exit) if element.exit else None,
        do_activity=copy_element(element.doActivity) if element.doActivity else None,
    )


@paste.register
def paste_state(copy_data: StateCopy, diagram, lookup):
    if copy_data.entry:
        paste_element(copy_data.entry, diagram, lookup)
    if copy_data.exit:
        paste_element(copy_data.exit, diagram, lookup)
    if copy_data.do_activity:
        paste_element(copy_data.do_activity, diagram, lookup)
    return paste_element(copy_data.state, diagram, lookup)


class TransitionCopy(NamedTuple):
    transition: ElementCopy
    guard: Optional[ElementCopy]


@copy.register
def copy_transition(element: Transition):
    return TransitionCopy(
        transition=copy_element(element),
        guard=copy_element(element.guard) if element.guard else None,
    )


@paste.register
def paste_transition(copy_data: TransitionCopy, diagram, lookup):
    if copy_data.guard:
        paste_element(copy_data.guard, diagram, lookup)
    return paste_element(copy_data.transition, diagram, lookup)
