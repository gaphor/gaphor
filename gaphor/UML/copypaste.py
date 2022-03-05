from __future__ import annotations

from typing import Iterator, NamedTuple

from gaphor.core.modeling.element import Id
from gaphor.diagram.copypaste import (
    ElementCopy,
    copy,
    copy_element,
    paste,
    paste_element,
)
from gaphor.UML.recipes import owner_package
from gaphor.UML.uml import NamedElement, Relationship


class NamedElementCopy(NamedTuple):
    element_copy: ElementCopy
    with_namespace: bool


def copy_named_element(
    element: NamedElement, blacklist: list[str] | None = None
) -> NamedElementCopy:
    return NamedElementCopy(
        element_copy=copy_element(element, blacklist),
        with_namespace=bool(element.namespace),
    )


@copy.register
def _copy_named_element(element: NamedElement) -> Iterator[tuple[Id, NamedElementCopy]]:
    yield element.id, copy_named_element(element)


def paste_named_element(copy_data: NamedElementCopy, diagram, lookup):
    paster = paste_element(
        copy_data.element_copy,
        diagram,
        lookup,
        filter=lambda n, v: not isinstance(v, Relationship),
    )
    element = next(paster)
    yield element
    next(paster, None)
    if copy_data.with_namespace and not element.namespace:
        element.package = owner_package(diagram.owner)


paste.register(NamedElementCopy, paste_named_element)
