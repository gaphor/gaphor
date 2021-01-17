"""Copy and paste data based on an element's `save()` and `load()` methods.

The `copy()` function will return all values serialized, either as string
values or reference id's.

The `paste()` function will resolve those values. Based on the elements
that are already in the model,

The copy() function returns only data that has to be part of the copy buffer.
the `paste()` function will load this data in a model.
"""

from __future__ import annotations

import itertools
from functools import singledispatch
from typing import (
    Callable,
    Dict,
    Iterator,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

import gaphas

from gaphor.core.modeling import Diagram, NamedElement, Presentation
from gaphor.core.modeling.collection import collection
from gaphor.core.modeling.element import Element, Id

Opaque = object


@singledispatch
def copy(obj: Element) -> Iterator[Tuple[Id, Opaque]]:
    """Create a copy of an element (or list of elements).

    The returned type should be distinct, so the `paste()` function can
    properly dispatch.
    """
    raise ValueError(f"No copier for {obj}")


@singledispatch
def paste(copy_data: Opaque, diagram: Diagram, lookup: Callable[[str], Element]):
    """Paste previously copied data.

    Based on the data type created in the `copy()` function, try to
    duplicate the copied elements.
    """
    raise ValueError(f"No paster for {copy_data}")


def serialize(value):
    if isinstance(value, (Element, gaphas.Item)):
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
    cls: Type[Element]
    id: Union[str, bool]
    data: Dict[str, Tuple[str, str]]


def copy_element(element: Element) -> ElementCopy:
    data = {}

    def save_func(name, value):
        # do not copy Element.presentation, to avoid cyclic dependencies
        if name != "presentation":
            data[name] = serialize(value)

    element.save(save_func)
    return ElementCopy(cls=element.__class__, id=element.id, data=data)


@copy.register
def _copy_element(element: Element) -> Iterator[Tuple[Id, ElementCopy]]:
    yield element.id, copy_element(element)


def paste_element(copy_data: ElementCopy, diagram, lookup):
    cls, id, data = copy_data
    element = diagram.model.create_as(cls, id)
    yield element
    for name, ser in data.items():
        for value in deserialize(ser, lookup):
            element.load(name, value)
    element.postload()


paste.register(ElementCopy, paste_element)


class NamedElementCopy(NamedTuple):
    element_copy: ElementCopy
    with_namespace: bool


def copy_named_element(element: NamedElement) -> NamedElementCopy:
    return NamedElementCopy(
        element_copy=copy_element(element), with_namespace=bool(element.namespace)
    )


@copy.register
def _copy_named_element(element: NamedElement) -> Iterator[Tuple[Id, NamedElementCopy]]:
    yield element.id, copy_named_element(element)


def paste_named_element(copy_data: NamedElementCopy, diagram, lookup):
    paster = paste_element(copy_data.element_copy, diagram, lookup)
    element = next(paster)
    yield element
    next(paster, None)
    if copy_data.with_namespace and not element.namespace:
        element.package = diagram.namespace


paste.register(NamedElementCopy, paste_named_element)


class PresentationCopy(NamedTuple):
    cls: Type[Element]
    data: Dict[str, Tuple[str, str]]
    parent: Optional[str]


def copy_presentation(item: Presentation) -> PresentationCopy:
    assert item.diagram
    data = {}

    def save_func(name, value):
        # Do not copy diagram, it's set when pasted,
        # parent and children are set separately.
        if name not in ("diagram", "parent", "children"):
            data[name] = serialize(value)

    item.save(save_func)
    parent = item.parent
    return PresentationCopy(
        cls=item.__class__,
        data=data,
        parent=parent.id if parent and isinstance(parent.id, str) else None,
    )


@copy.register
def _copy_presentation(item: Presentation) -> Iterator[Tuple[Id, object]]:
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
    elements: Dict[str, object]


@copy.register
def _copy_all(items: set) -> CopyData:
    elements = itertools.chain.from_iterable(copy(item) for item in items)
    return CopyData(elements=dict(elements))


@paste.register
def _paste_all(copy_data: CopyData, diagram, lookup) -> Set[Presentation]:
    new_elements: Dict[str, Optional[Presentation]] = {}

    def element_lookup(ref: str):
        if ref in new_elements:
            return new_elements[ref]

        looked_up = lookup(ref)
        if looked_up:
            return looked_up

        elif ref in copy_data.elements:
            paster = paste(copy_data.elements[ref], diagram, element_lookup)
            new_elements[ref] = next(paster)
            next(paster, None)
            return new_elements[ref]

        looked_up = diagram.lookup(ref)
        if looked_up:
            return looked_up

    for old_id, data in copy_data.elements.items():
        if old_id in new_elements:
            continue
        element_lookup(old_id)

    for element in new_elements.values():
        assert element
        element.postload()

    return set(e for e in new_elements.values() if isinstance(e, Presentation))
