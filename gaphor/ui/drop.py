from __future__ import annotations

from functools import singledispatch

from gaphor import UML
from gaphor.core.modeling import Diagram, Element
from gaphor.diagram.presentation import postload_connect
from gaphor.diagram.support import get_diagram_item, get_diagram_item_metadata


@singledispatch
def drop(element: Element, diagram: Diagram, x: float, y: float):
    if item_class := get_diagram_item(type(element)):
        item = diagram.create(item_class)
        assert item

        item.matrix.translate(x, y)
        item.subject = element

        return item
    return None


@drop.register
def drop_relationship(element: UML.Relationship, diagram, x, y):
    item_class = get_diagram_item(type(element))
    if not item_class:
        return None

    metadata = get_diagram_item_metadata(item_class)
    if not metadata:
        return None

    head_item = diagram_has_presentation(diagram, metadata["head"].get(element))
    tail_item = diagram_has_presentation(diagram, metadata["tail"].get(element))
    if not head_item or not tail_item:
        return None

    item = diagram.create(item_class)
    assert item

    item.matrix.translate(x, y)
    item.subject = element

    postload_connect(item, item.head, head_item)
    postload_connect(item, item.tail, tail_item)

    return item


def diagram_has_presentation(diagram, element):
    return next((p for p in element.presentation if p.diagram is diagram), None)


@drop.register
def drop_association(element: UML.Association, diagram, x, y):
    return None
