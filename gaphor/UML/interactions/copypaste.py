from gaphor.diagram.copypaste import copy
from gaphor.UML import ExecutionSpecification, Message
from gaphor.UML.copypaste import copy_named_element


@copy.register
def copy_message(element: Message):
    yield element.id, copy_named_element(element)
    if element.sendEvent:
        yield from copy(element.sendEvent)
    if element.receiveEvent:
        yield from copy(element.receiveEvent)


@copy.register
def copy_execution_specification(element: ExecutionSpecification):
    yield element.id, copy_named_element(element)
    for occurrence in element.executionOccurrenceSpecification:
        yield from copy(occurrence)
