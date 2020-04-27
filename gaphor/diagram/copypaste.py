"""
Copy and paste data based on an element's `save()` and `load()` methods.

The `copy()` function will return all values serialized, either as string
values or reference id's.

The `paste()` function will resolve those values. Based on the elements
that are already in the model,

The copy() function returns only data that has to be part of the copy buffer.
the `paste()` function will load this data in a model.
"""

from functools import singledispatch
from typing import Callable, Dict, List, NamedTuple, Tuple, Type, TypeVar

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


class PresentationCopy(NamedTuple):
    cls: Type[Element]
    data: Dict[str, Tuple[str, str]]


@copy.register
def _copy_presentation(item: Presentation) -> PresentationCopy:
    buffer = {}

    def save_func(name, value):
        if isinstance(value, (Element, gaphas.Item)):
            buffer[name] = ("r", value.id)
        else:
            assert not isinstance(value, collection)
            if isinstance(value, bool):
                value = int(value)
            buffer[name] = ("v", str(value))

    item.save(save_func)
    return PresentationCopy(cls=item.__class__, data=buffer)


@paste.register
def _paste_presentation(copy_data: PresentationCopy, diagram, lookup):
    cls, data = copy_data
    item = diagram.create(cls)
    for key, (vtype, value) in data.items():
        if vtype == "r":
            other = lookup(value)
            if other:
                item.load(key, other)
        elif vtype == "v":
            item.load(key, value)
    item.canvas.update_matrices([item])
    item.postload()
    return item


class ListOfData(NamedTuple):
    data: Dict[str, object]


@copy.register
def _copy_all(items: set) -> ListOfData:
    return ListOfData(data={item.id: copy(item) for item in items})


@paste.register
def _paste_all(copy_data: ListOfData, diagram, lookup):
    new_data: Dict[str, Element] = {}

    def _lookup(ref: str):
        if ref in new_data:
            return new_data[ref]
        elif ref in copy_data.data:
            new_data[ref] = paste(copy_data.data[ref], diagram, _lookup)
            return new_data[ref]
        else:
            return lookup(ref)

    for old_id, data in copy_data.data.items():
        new_data[old_id] = paste(data, diagram, _lookup)

    return set(new_data.values())
