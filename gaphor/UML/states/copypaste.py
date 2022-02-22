from gaphor.diagram.copypaste import copy
from gaphor.UML import State, Transition
from gaphor.UML.copypaste import copy_named_element


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
