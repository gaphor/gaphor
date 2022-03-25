from __future__ import annotations

from gaphor import UML
from gaphor.diagram.drop import drop
from gaphor.diagram.presentation import postload_connect
from gaphor.diagram.support import get_diagram_item, get_diagram_item_metadata


@drop.register
def drop_relationship(element: UML.Relationship, diagram, x, y):
    item_class = get_diagram_item(type(element))
    if not item_class:
        return None

    metadata = get_diagram_item_metadata(item_class)
    if not metadata:
        return None

    return _drop(
        element,
        metadata["head"].get(element),
        metadata["tail"].get(element),
        diagram,
        x,
        y,
    )


def diagram_has_presentation(diagram, element):
    return next((p for p in element.presentation if p.diagram is diagram), None)


@drop.register
def drop_association(element: UML.Association, diagram, x, y):
    return _drop(
        element, element.memberEnd[0].type, element.memberEnd[1].type, diagram, x, y
    )


@drop.register
def drop_connector(element: UML.Connector, diagram, x, y):
    return _drop(element, element.end[0].role, element.end[1].role, diagram, x, y)


@drop.register
def drop_message(element: UML.Message, diagram, x, y):
    assert isinstance(element.sendEvent, UML.MessageOccurrenceSpecification)
    assert isinstance(element.receiveEvent, UML.MessageOccurrenceSpecification)
    return _drop(
        element, element.sendEvent.covered, element.receiveEvent.covered, diagram, x, y
    )


def _drop(element, head_element, tail_element, diagram, x, y):
    item_class = get_diagram_item(type(element))
    if not item_class:
        return None

    head_item = diagram_has_presentation(diagram, head_element)
    tail_item = diagram_has_presentation(diagram, tail_element)
    if not head_item or not tail_item:
        return None

    item = diagram.create(item_class)
    assert item

    item.matrix.translate(x, y)
    item.subject = element

    postload_connect(item, item.head, head_item)
    postload_connect(item, item.tail, tail_item)

    return item
