"""
Copy and paste data based on an element's `save()` and `load()` methods.

The `copy()` function will return all values serialized, either as string
values or reference id's.

The `paste()` function will resolve those values. Based on the elements
that are already in the model,
"""

from functools import singledispatch
from typing import Callable, Dict, NamedTuple, Tuple, Type

import gaphas

from gaphor.core.modeling import Element, Presentation
from gaphor.core.modeling.collection import collection


@singledispatch
def copy(obj):
    raise ValueError(f"No copier for {obj}")


@singledispatch
def paste(diagram, copy_data, lookup: Callable[[str], Element]):
    raise ValueError(f"No paster for {copy_data}")


class PresentationCopy(NamedTuple):
    cls: Type[Element]
    data: Dict[str, Tuple[str, str]]


@copy.register(Presentation)
def _copy_presentation(item):
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


@paste.register(PresentationCopy)
def _paste_presentation(copy_data: PresentationCopy, diagram, lookup):
    cls, data = copy_data
    item = diagram.create(cls)
    for key, (vtype, value) in data.items():
        if vtype == "r":
            other = lookup(value)
            item.load(key, other)
        elif vtype == "v":
            item.load(key, value)
    item.postload()
