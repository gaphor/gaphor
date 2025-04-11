from __future__ import annotations

import logging
from collections.abc import Callable

from gaphas.geometry import Rectangle
from gaphas.item import NW, SE
from generic.multidispatch import FunctionDispatcher, multidispatch

from gaphor.core.modeling import Base, Diagram, Presentation
from gaphor.diagram.group import change_owner, ungroup
from gaphor.diagram.presentation import ElementPresentation, connect
from gaphor.diagram.support import get_diagram_item

log = logging.getLogger(__name__)


def no_drop(element: Base, diagram: Diagram, x: float, y: float):
    return None


drop: FunctionDispatcher[Callable[[Base, Base, float, float], Presentation | None]] = (
    multidispatch(Base, Diagram)(no_drop)
)
"""Drop an element on a diagram or presentation

The position (x, y) is in parent element coordinates.
"""


@drop.register(Presentation, Diagram)
def drop_presentation(item: Presentation, diagram: Diagram, x: float, y: float):
    if item.diagram is not diagram:
        return

    old_parent = item.parent

    if old_parent and ungroup(old_parent.subject, item.subject):
        item.change_parent(None)
        old_parent.request_update()


@drop.register(Presentation, Presentation)
def drop_on_presentation(
    item: Presentation, new_parent: Presentation, x: float, y: float
):
    """Place :obj:`item`, with position (:obj:`x`, :obj:`y`) relative to :obj:`new_parent`."""
    assert item.diagram is new_parent.diagram

    old_parent = item.parent

    if new_parent is old_parent:
        if old_parent is not None:
            old_parent.request_update()
        return

    if old_parent and ungroup(old_parent.subject, item.subject):
        item.change_parent(None)
        old_parent.request_update()

    if new_parent and item.subject and change_owner(new_parent.subject, item.subject):
        grow_parent(new_parent, item)
        item.change_parent(new_parent)


def grow_parent(parent: Presentation, item: Presentation) -> None:
    if not isinstance(item, ElementPresentation):
        return

    if not isinstance(parent, ElementPresentation):
        log.warning(f"Can not grow item {parent}: not an ElementPresentation")
        return

    parent_bb = _bounds(parent)
    item_bb = _bounds(item)
    item_bb.expand(20)
    new_parent_bb = parent_bb + item_bb

    c2i = parent.matrix_i2c.inverse()
    parent.handles()[NW].pos = c2i.transform_point(new_parent_bb.x, new_parent_bb.y)
    parent.handles()[SE].pos = c2i.transform_point(new_parent_bb.x1, new_parent_bb.y1)


def _bounds(item: ElementPresentation) -> Rectangle:
    transform = item.matrix_i2c.transform_point
    x0, y0 = transform(*item.handles()[NW].pos)
    x1, y1 = transform(*item.handles()[SE].pos)
    return Rectangle(x0, y0, x1=x1, y1=y1)


def drop_relationship(
    element: Base,
    head_element: Base | None,
    tail_element: Base | None,
    diagram: Diagram,
    x: float,
    y: float,
) -> Presentation | None:
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


def diagram_has_presentation(diagram: Diagram, element: Base | None):
    return (
        next((p for p in element.presentation if p.diagram is diagram), None)
        if element
        else None
    )
