from gaphor.diagram.copypaste import copy, copy_named_element
from gaphor.UML import State, Transition


@copy.register
def copy_state(element: State):
    yield element.id, copy_named_element(element)
    if element.entry:
        yield from copy(element.entry)
    if element.exit:
        yield from copy(element.exit)
    if element.doActivity:
        yield from copy(element.doActivity)


@copy.register
def copy_transition(element: Transition):
    yield element.id, copy_named_element(element)
    if element.guard:
        yield from copy(element.guard)
