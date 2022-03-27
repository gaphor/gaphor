from __future__ import annotations

from functools import singledispatch

from gaphor.core.modeling import Diagram, Element, Presentation
from gaphor.diagram.support import get_diagram_item


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
def drop_presentation(element: Presentation, diagram: Diagram, x: float, y: float):
    return None
