from __future__ import annotations

from collections.abc import Iterator
from typing import NamedTuple

from gaphor.core.modeling import Id
from gaphor.diagram.copypaste import (
    BaseCopy,
    Opaque,
    copy,
    copy_diagram,
    copy_element,
    paste,
    paste_element,
)
from gaphor.UML.recipes import owner_package
from gaphor.UML.uml import (
    Diagram,
    MultiplicityElement,
    NamedElement,
    Package,
    Relationship,
    Slot,
    Type,
)


def copy_multiplicity(
    element: MultiplicityElement, blacklist: list[str] | None = None
) -> Iterator[tuple[Id, Opaque]]:
    if element.lowerValue:
        yield from copy(element.lowerValue)
    if element.upperValue:
        yield from copy(element.upperValue)


class NamedElementCopy(NamedTuple):
    element_copy: BaseCopy


def copy_named_element(
    element: NamedElement, blacklist: list[str] | None = None
) -> NamedElementCopy:
    return NamedElementCopy(
        element_copy=copy_element(element, blacklist),
    )


@copy.register
def _copy_named_element(element: NamedElement) -> Iterator[tuple[Id, NamedElementCopy]]:
    yield element.id, copy_named_element(element)


@copy.register
def _copy_diagram(element: Diagram) -> Iterator[tuple[Id, Opaque]]:
    yield from copy_diagram(element)


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
        isinstance(element, Type | Package)
        and (not element.namespace)
        and (package := owner_package(diagram.owner)) is not element
    ):
        if isinstance(element, Package):
            element.nestingPackage = package
        else:
            element.package = package


paste.register(NamedElementCopy, paste_named_element)


@copy.register
def copy_slot(element: Slot):
    yield element.id, copy_element(element)
    if element.value:
        yield from copy(element.value)
