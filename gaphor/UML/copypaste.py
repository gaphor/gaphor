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
from gaphor.UML.uml import NamedElement, Package, Relationship, Type


class NamedElementCopy(NamedTuple):
    element_copy: ElementCopy


def copy_named_element(
    element: NamedElement, blacklist: list[str] | None = None
) -> NamedElementCopy:
    return NamedElementCopy(
        element_copy=copy_element(element, blacklist),
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
    if (
        not element.namespace
        and isinstance(element, (Type, Package))
        and (package := owner_package(diagram.owner)) is not element
    ):
        element.package = package


paste.register(NamedElementCopy, paste_named_element)
