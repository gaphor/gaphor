"""
Copy and paste data based on an element's `save()` and `load()` methods.

The `copy()` function will return all values serialized, either as string
values or reference id's.

The `paste()` function will resolve those values. Based on the elements
that are already in the model,

The copy() function returns only data that has to be part of the copy buffer.
the `paste()` function will load this data in a model.
"""

from __future__ import annotations

from functools import singledispatch
from typing import Callable, Dict, List, NamedTuple, Set, Tuple, Type, TypeVar

import gaphas

from gaphor.core.modeling import Diagram, Element, Presentation
from gaphor.core.modeling.collection import collection

T = TypeVar("T")


@singledispatch
def copy(obj: Element) -> T:
    """
    Create a copy of an element (or list of elements).
    The returned type should be distinct, so the `paste()`
    function can properly dispatch.
    """
    raise ValueError(f"No copier for {obj}")


@singledispatch
def paste(copy_data: T, diagram: Diagram, lookup: Callable[[str], Element]):
    """
    Paste previously copied data. Based on the data type created in the
    `copy()` function, try to duplicate the copied elements.
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
        return lookup(value)
    elif vtype == "c":
        return [deserialize(v, lookup) for v in value]
    elif vtype == "v":
        return value


class ElementCopy(NamedTuple):
    cls: Type[Element]
    data: Dict[str, Tuple[str, str]]


@copy.register
def _copy_element(item: Element) -> ElementCopy:
    buffer = {}

    def save_func(name, value):
        buffer[name] = serialize(value)

    item.save(save_func)
    return ElementCopy(cls=item.__class__, data=buffer)


@paste.register
def _paste_element(copy_data: ElementCopy, diagram, lookup):
    cls, data = copy_data
    item = diagram.create(cls)
    for name, ser in data.items():
        value = deserialize(ser, lookup)
        if value is not None:
            item.load(name, value)
    item.canvas.update_matrices([item])
    item.postload()
    return item


class CopyData(NamedTuple):
    items: Dict[str, object]
    elements: Dict[str, object]


@copy.register
def _copy_all(items: set) -> CopyData:
    return CopyData(
        items={item.id: copy(item) for item in items},
        elements={
            item.subject.id: copy(item.subject)
            for item in items
            if isinstance(item, Presentation) and item.subject
        },
    )


@paste.register
def _paste_all(copy_data: CopyData, diagram, lookup) -> Set[Presentation]:
    new_items: Dict[str, Presentation] = {}

    def _lookup(ref: str):
        if ref in new_items:
            return new_items[ref]
        elif ref in copy_data.items:
            new_items[ref] = paste(copy_data.items[ref], diagram, _lookup)
            return new_items[ref]
        else:
            return lookup(ref)

    for old_id, data in copy_data.items.items():
        new_items[old_id] = paste(data, diagram, _lookup)

    return set(new_items.values())
