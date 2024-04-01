from __future__ import annotations

from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.diagram.drop import drop
from gaphor.diagram.presentation import connect
from gaphor.diagram.support import get_diagram_item, get_diagram_item_metadata


@drop.register(UML.Relationship, Diagram)
def drop_relationship(element: UML.Relationship, diagram: Diagram, x, y):
    item_class = get_diagram_item(type(element))
    if not item_class:
        return None

    metadata = get_diagram_item_metadata(item_class)
    return (
        _drop(
            element,
            metadata["head"].get(element),
            metadata["tail"].get(element),
            diagram,
            x,
            y,
        )
        if metadata
        else None
    )


def diagram_has_presentation(diagram, element):
    return (
        next((p for p in element.presentation if p.diagram is diagram), None)
        if element
        else None
    )


@drop.register(UML.Association, Diagram)
def drop_association(element: UML.Association, diagram: Diagram, x, y):
    return _drop(
        element, element.memberEnd[0].type, element.memberEnd[1].type, diagram, x, y
    )


@drop.register(UML.Connector, Diagram)
def drop_connector(element: UML.Connector, diagram: Diagram, x, y):
    return _drop(element, element.end[0].role, element.end[1].role, diagram, x, y)


@drop.register(UML.Message, Diagram)
def drop_message(element: UML.Message, diagram: Diagram, x, y):
    return _drop(
        element,
        element.sendEvent.covered
        if isinstance(element.sendEvent, UML.MessageOccurrenceSpecification)
        else None,
        element.receiveEvent.covered
        if isinstance(element.receiveEvent, UML.MessageOccurrenceSpecification)
        else None,
        diagram,
        x,
        y,
    )


def _drop(element, head_element, tail_element, diagram, x, y):
    item_class = get_diagram_item(type(element))
    if not item_class:
        return None

    head_item = diagram_has_presentation(diagram, head_element)
    tail_item = diagram_has_presentation(diagram, tail_element)
    if (head_element and not head_item) or (tail_element and not tail_item):
        return None

    item = diagram.create(item_class)
    assert item

    item.matrix.translate(x, y)
    item.subject = element

    if head_item:
        connect(item, item.head, head_item)
    if tail_item:
        connect(item, item.tail, tail_item)

    return item
