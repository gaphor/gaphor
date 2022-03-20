from __future__ import annotations

from functools import singledispatch

from gaphor import UML
from gaphor.core.modeling import Element
from gaphor.diagram.support import get_diagram_item


@singledispatch
def drop(element: Element, diagram, x, y):
    return None


@drop.register
def drop_namespace(element: UML.Namespace, diagram, x, y):
    if item_class := get_diagram_item(type(element)):
        item = diagram.create(item_class)
        assert item

        item.matrix.translate(x, y)
        item.subject = element

        return item
    return None


@drop.register
def drop_association(element: UML.Association, diagram, x, y):
    return None
