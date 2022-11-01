from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from gaphor.core.modeling import Element, ElementFactory
from gaphor.core.modeling.collection import collection

ADD = 1
REMOVE = 2


@dataclass
class ElementChange:
    type: int
    element_id: str
    element_name: str
    element_type: object


@dataclass
class ValueChange:
    type: int
    element_id: str
    property_name: str
    property_value: object


@dataclass
class RefChange:
    type: int
    element_id: str
    property_name: str
    property_ref: str


@dataclass
class ChangeSet:
    changes: list[ElementChange | ValueChange | RefChange]


def compare(
    current: ElementFactory, incoming: ElementFactory
) -> Iterable[ElementChange | ValueChange | RefChange]:
    current_keys = set(current.keys())
    incoming_keys = set(incoming.keys())

    for key in current_keys.difference(incoming_keys):
        e = current.lookup(key)
        yield ElementChange(
            type=REMOVE,
            element_name=type(e).__name__,
            element_type=type(e),
            element_id=key,
        )

    for key in incoming_keys.difference(current_keys):
        e = incoming[key]
        yield ElementChange(
            type=ADD,
            element_name=type(e).__name__,
            element_type=type(e),
            element_id=key,
        )
        yield from added_properties(e)


def added_properties(element: Element):
    changes: list[ValueChange | RefChange] = []

    def save_func(name, value):
        if isinstance(value, Element):
            changes.append(
                RefChange(
                    type=ADD,
                    element_id=element.id,
                    property_name=name,
                    property_ref=value.id,
                )
            )
        elif isinstance(value, collection):
            changes.extend(
                RefChange(
                    type=ADD,
                    element_id=element.id,
                    property_name=name,
                    property_ref=v.id,
                )
                for v in value
            )
        else:
            changes.append(
                ValueChange(
                    type=ADD,
                    element_id=element.id,
                    property_name=name,
                    property_value=value,
                )
            )

    for property in element.umlproperties():
        property.save(element, save_func)

    yield from changes
