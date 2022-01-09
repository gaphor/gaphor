"""Copy and paste data based on an element's `save()` and `load()` methods.

The `copy()` function will return all values serialized, either as string
values or reference id's.

The `paste_link()` function will resolve those values and place instances of
them on the diagram using the same defining element.
The `paste_full()` function is similar, but it creates new defining elements
for the elements being pasted.

The `copy()` function returns only data that has to be part of the copy buffer.
the `paste()` function will load this data in a model.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterable
from functools import singledispatch
from typing import Callable, Iterator, NamedTuple

from gaphor.core.modeling import Diagram, Presentation
from gaphor.core.modeling.collection import collection
from gaphor.core.modeling.element import Element, Id
from gaphor.UML import NamedElement
from gaphor.UML.recipes import owner_package

Opaque = object


@singledispatch
def copy(obj: Element | Iterable) -> Iterator[tuple[Id, Opaque]]:
    """Create a copy of an element (or list of elements).

    The returned type should be distinct, so the `paste()` function can
    properly dispatch.
    """
    raise ValueError(f"No copier for {obj}")


def paste_link(copy_data, diagram, lookup) -> set[Presentation]:
    return _paste(copy_data, diagram, lookup, full=False)


def paste_full(copy_data, diagram, lookup) -> set[Presentation]:
    return _paste(copy_data, diagram, lookup, full=True)


@singledispatch
def paste(copy_data: Opaque, diagram: Diagram, lookup: Callable[[str], Element]):
    """Paste previously copied data.

    Based on the data type created in the `copy()` function, try to
    duplicate the copied elements.
    """
    raise ValueError(f"No paster for {copy_data}")


def serialize(value):
    if isinstance(value, Element):
        return ("r", value.id)
    elif isinstance(value, collection):
        return ("c", [serialize(v) for v in value])
    else:
        if isinstance(value, bool):
            value = int(value)
        return ("v", str(value))


def deserialize(ser, lookup):
    vtype, value = ser
    if vtype == "r":
        e = lookup(value)
        if e:
            yield e
    elif vtype == "c":
        for v in value:
            yield from deserialize(v, lookup)
    elif vtype == "v":
        yield value


class ElementCopy(NamedTuple):
    cls: type[Element]
    id: str | bool
    data: dict[str, tuple[str, str]]


def copy_element(element: Element, blacklist: list[str] | None = None) -> ElementCopy:
    data = {}
    # do not copy Element.presentation, to avoid cyclic dependencies
    blacklist_ = blacklist + ["presentation"] if blacklist else ["presentation"]

    def save_func(name, value):
        if name not in blacklist_:
            data[name] = serialize(value)

    element.save(save_func)
    return ElementCopy(cls=element.__class__, id=element.id, data=data)


@copy.register
def _copy_element(element: Element) -> Iterator[tuple[Id, ElementCopy]]:
    yield element.id, copy_element(element)


def paste_element(copy_data: ElementCopy, diagram, lookup):
    cls, _id, data = copy_data
    element = diagram.model.create(cls)
    yield element
    for name, ser in data.items():
        for value in deserialize(ser, lookup):
            element.load(name, value)
    element.postload()


paste.register(ElementCopy, paste_element)


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
    paster = paste_element(copy_data.element_copy, diagram, lookup)
    element = next(paster)
    yield element
    next(paster, None)
    if copy_data.with_namespace and not element.namespace:
        element.package = owner_package(diagram.owner)


paste.register(NamedElementCopy, paste_named_element)


@copy.register
def _copy_diagram(element: Diagram) -> Iterator[tuple[Id, ElementCopy]]:
    yield element.id, copy_element(element, blacklist=["ownedPresentation"])


class PresentationCopy(NamedTuple):
    cls: type[Element]
    data: dict[str, tuple[str, str]]
    parent: str | None


def copy_presentation(item: Presentation) -> PresentationCopy:
    assert item.diagram

    parent = item.parent
    return PresentationCopy(
        cls=item.__class__,
        data=copy_element(item, blacklist=["diagram", "parent", "children"]).data,
        parent=parent.id if parent else None,
    )


@copy.register
def _copy_presentation(item: Presentation) -> Iterator[tuple[Id, object]]:
    yield item.id, copy_presentation(item)
    if item.subject:
        yield from copy(item.subject)


@paste.register
def paste_presentation(copy_data: PresentationCopy, diagram, lookup):
    cls, data, parent = copy_data
    item = diagram.create(cls)
    yield item
    if parent:
        p = lookup(parent)
        if p:
            item.parent = p

    for name, ser in data.items():
        for value in deserialize(ser, lookup):
            item.load(name, value)
    diagram.update_now((), [item])


class CopyData(NamedTuple):
    elements: dict[str, object]


@copy.register  # type: ignore[arg-type]
def _copy_all(items: Iterable) -> CopyData:
    elements = itertools.chain.from_iterable(copy(item) for item in items)
    return CopyData(elements=dict(elements))


def _paste(copy_data, diagram, lookup, full) -> set[Presentation]:
    assert isinstance(copy_data, CopyData)

    new_elements: dict[str, Presentation | None] = {}

    def element_lookup(ref: str):
        if ref in new_elements:
            return new_elements[ref]

        looked_up = lookup(ref)
        if not full and looked_up and not isinstance(looked_up, Presentation):
            return looked_up

        if ref in copy_data.elements:
            paster = paste(copy_data.elements[ref], diagram, element_lookup)
            new_elements[ref] = next(paster)
            next(paster, None)
            return new_elements[ref]

        if full and looked_up and not isinstance(looked_up, Presentation):
            return looked_up

        looked_up = diagram.lookup(ref)
        if looked_up:
            return looked_up

    for old_id in copy_data.elements.keys():
        if old_id in new_elements:
            continue
        element_lookup(old_id)

    for element in new_elements.values():
        assert element
        element.postload()

    return {e for e in new_elements.values() if isinstance(e, Presentation)}
