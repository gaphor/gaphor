import itertools
from typing import List, NamedTuple, Optional

from gaphor.diagram.copypaste import (
    ElementCopy,
    copy,
    copy_element,
    paste,
    paste_element,
)
from gaphor.UML import ExecutionSpecification, Message


class MessageCopy(NamedTuple):
    element_copy: ElementCopy
    send_event: Optional[ElementCopy]
    receive_event: Optional[ElementCopy]


@copy.register
def copy_message(element: Message):
    return MessageCopy(
        element_copy=copy_element(element),
        send_event=copy_element(element.sendEvent) if element.sendEvent else None,
        receive_event=copy_element(element.receiveEvent)
        if element.receiveEvent
        else None,
    )


@paste.register
def paste_message(copy_data: MessageCopy, diagram, lookup):
    if copy_data.send_event:
        paste_element(copy_data.send_event, diagram, lookup)
    if copy_data.receive_event:
        paste_element(copy_data.receive_event, diagram, lookup)
    return paste_element(copy_data.element_copy, diagram, lookup)


class ExecutionSpecificationCopy(NamedTuple):
    element_copy: ElementCopy
    occurrences: List[ElementCopy]


@copy.register
def copy_execution_specification(element: ExecutionSpecification):
    return ExecutionSpecificationCopy(
        element_copy=copy_element(element),
        occurrences=[
            copy_element(occurrence)
            for occurrence in element.executionOccurrenceSpecification
        ],
    )


@paste.register
def paste_execution_specification(
    copy_data: ExecutionSpecificationCopy, diagram, lookup
):
    for occurrence in copy_data.occurrences:
        paste_element(occurrence, diagram, lookup)
    return paste_element(copy_data.element_copy, diagram, lookup)
