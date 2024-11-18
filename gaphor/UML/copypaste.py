from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import NamedTuple

from gaphor.core.modeling import Id
from gaphor.diagram.copypaste import Opaque, copy, copy_base, deserialize, paste
from gaphor.UML.recipes import owner_package
from gaphor.UML.uml import Diagram, Element, NamedElement, Package, Relationship, Type


class ElementCopy(NamedTuple):
    cls: type[Element]
    id: Id
    data: dict[str, tuple[str, str]]


def copy_element(element: Element, blacklist: list[str] | None = None) -> ElementCopy:
    data = copy_base(
        element, blacklist + ["presentation"] if blacklist else ["presentation"]
    )
    return ElementCopy(cls=element.__class__, id=element.id, data=data)


@copy.register
def _copy_element(element: Element) -> Iterator[tuple[Id, ElementCopy]]:
    yield element.id, copy_element(element)


def paste_element(
    copy_data: ElementCopy,
    diagram,
    lookup,
    filter: Callable[[str, str | int | Element], bool] | None = None,
) -> Iterator[Element]:
    cls, _id, data = copy_data
    element = diagram.model.create(cls)
    yield element
    for name, ser in data.items():
        for value in deserialize(ser, lookup):
            if not filter or filter(name, value):
                element.load(name, value)
    element.postload()


paste.register(ElementCopy, paste_element)


@copy.register
def _copy_diagram(element: Diagram) -> Iterator[tuple[Id, Opaque]]:
    assert isinstance(element, Element)
    yield element.id, copy_element(element, blacklist=["ownedPresentation"])
    for presentation in element.ownedPresentation:
        if presentation.subject is element:
            continue
        yield from copy(presentation)


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
        isinstance(element, Type | Package)
        and (not element.namespace)
        and (package := owner_package(diagram.owner)) is not element
    ):
        element.package = package


paste.register(NamedElementCopy, paste_named_element)
