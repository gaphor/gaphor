from __future__ import annotations

from gaphor import UML
from gaphor.core.modeling import Base, Diagram
from gaphor.diagram.drop import (
    diagram_has_presentation,
    drop,
    drop_relationship,
    grow_parent,
)
from gaphor.diagram.group import change_owner
from gaphor.diagram.presentation import ElementPresentation, Presentation, connect
from gaphor.diagram.support import get_diagram_item, get_diagram_item_metadata


@drop.register(UML.Element, Diagram)
def drop_element(
    element: UML.Element, diagram: Diagram, x: float, y: float
) -> Presentation | None:
    if item_class := get_diagram_item(type(element)):
        item = diagram.create(item_class)
        assert item

        item.matrix.translate(x, y)
        item.subject = element

        return item
    return None


@drop.register(UML.Association, Diagram)
def drop_association(element: UML.Association, diagram: Diagram, x, y):
    return drop_relationship(
        element, element.memberEnd[0].type, element.memberEnd[1].type, diagram, x, y
    )


@drop.register(UML.Connector, Diagram)
def drop_connector(element: UML.Connector, diagram: Diagram, x, y):
    return drop_relationship(
        element, element.end[0].role, element.end[1].role, diagram, x, y
    )


@drop.register(UML.Message, Diagram)
def drop_message(element: UML.Message, diagram: Diagram, x, y):
    return drop_relationship(
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


@drop.register(UML.Pin, Diagram)
def drop_pin(element: UML.Pin, diagram: Diagram, x, y):
    return drop_pin_on_diagram(element, element.owner, diagram, x, y)


def drop_pin_on_diagram(
    element: Base, owner: Base | None, diagram: Diagram, x, y
) -> Presentation | None:
    item_class = get_diagram_item(type(element))
    if not item_class:
        return None

    owner_item = diagram_has_presentation(diagram, owner)
    if owner and not owner_item:
        return None

    item = diagram.create(item_class)
    assert item

    item.matrix.translate(x, y)
    item.subject = element
    handle = item.handles()[-1]
    if owner_item:
        connect(item, handle, owner_item)

    return item


@drop.register(UML.DirectedRelationship, Diagram)
def drop_relationship_on_diagram(
    element: UML.DirectedRelationship, diagram: Diagram, x: float, y: float
) -> Presentation | None:
    item_class = get_diagram_item(type(element))
    if not item_class:
        return None

    metadata = get_diagram_item_metadata(item_class)
    if metadata:
        # DirectedRelationships can be many-to-many, so we may need to create multiple items
        if metadata["head"].upper == 1 and metadata["tail"].upper == 1:
            head = metadata["head"].get(element)
            tail = metadata["tail"].get(element)
            new_item = drop_relationship(element, head, tail, diagram, x, y)
            if new_item:
                return new_item
        else:
            for head in metadata["head"].get(element):
                for tail in metadata["tail"].get(element):
                    new_item = drop_relationship(element, head, tail, diagram, x, y)
                    if new_item:
                        return new_item
    return None


@drop.register(UML.Element, ElementPresentation)
def drop_element_on_element_presentation(
    element: UML.Element, parent_item: ElementPresentation, x: float, y: float
) -> Presentation | None:
    item_class = get_diagram_item(type(element))
    if not item_class:
        return None

    diagram = parent_item.diagram
    item = diagram.create(item_class, subject=element)
    assert item

    if change_owner(parent_item.subject, element):
        item.parent = parent_item
        item.matrix.translate(x, y)
        grow_parent(parent_item, item)

    parent_item.request_update()

    return item
