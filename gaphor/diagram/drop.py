from __future__ import annotations

from typing import Callable

from generic.multidispatch import FunctionDispatcher, multidispatch

from gaphor.core.modeling import Diagram, Element, Presentation
from gaphor.diagram.support import get_diagram_item


def drop_element(element: Element, diagram: Diagram, x: float, y: float):
    if item_class := get_diagram_item(type(element)):
        item = diagram.create(item_class)
        assert item

        item.matrix.translate(x, y)
        item.subject = element

        return item
    return None


drop: FunctionDispatcher[Callable[[Element, Element], bool]] = multidispatch(
    Element, Diagram
)(drop_element)


@drop.register(Presentation, Diagram)
def drop_presentation(element: Presentation, diagram: Diagram, x: float, y: float):
    return None
