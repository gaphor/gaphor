from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from gaphor.core.modeling import Element, ElementFactory
from gaphor.core.modeling.collection import collection

ADD = 1
REMOVE = 2
UPDATE = 3


@dataclass
class ElementChange:
    op: int
    element_id: str
    element_name: str
    element_type: type[Element] | None


@dataclass
class ValueChange:
    op: int
    element_id: str
    property_name: str
    property_value: str | int


@dataclass
class RefChange:
    op: int
    element_id: str
    property_name: str
    property_ref: str


@dataclass
class ChangeSet:
    changes: list[ElementChange | ValueChange | RefChange]


class UnmatchableModel(Exception):
    def __init__(self, current, incoming):
        super().__init__(f"Incompatible types {current} != {incoming}")
        self.current = current
        self.incoming = incoming


def compare(
    current: ElementFactory, incoming: ElementFactory
) -> Iterable[ElementChange | ValueChange | RefChange]:
    current_keys = set(current.keys())
    incoming_keys = set(incoming.keys())

    for key in current_keys.difference(incoming_keys):
        e = current[key]
        yield ElementChange(
            op=REMOVE,
            element_name=type(e).__name__,
            element_type=type(e),
            element_id=key,
        )

    for key in incoming_keys.difference(current_keys):
        e = incoming[key]
        yield ElementChange(
            op=ADD,
            element_name=type(e).__name__,
            element_type=type(e),
            element_id=key,
        )
        yield from updated_properties(None, e)

    for key in current_keys.intersection(incoming_keys):
        c = current[key]
        i = incoming[key]
        if type(c) is not type(i):
            raise UnmatchableModel(c, i)
        yield from updated_properties(c, i)


def updated_properties(current, incoming):
    changes: list[ValueChange | RefChange] = []

    def save_func(name, value):
        other = getattr(current, name) if current else None
        if isinstance(value, Element):
            # Allow values to be None
            if (value and value.id) != (other and other.id):
                changes.append(
                    RefChange(
                        op=UPDATE if current else ADD,
                        element_id=incoming.id,
                        property_name=name,
                        property_ref=value.id,
                    )
                )
        elif isinstance(value, collection):
            value_ids = {v.id for v in value}
            other_ids = {o.id for o in other} if other else set()
            changes.extend(
                RefChange(
                    op=ADD,
                    element_id=incoming.id,
                    property_name=name,
                    property_ref=v.id,
                )
                for v in value
                if v.id not in other_ids
            )
            changes.extend(
                RefChange(
                    op=REMOVE,
                    element_id=incoming.id,
                    property_name=name,
                    property_ref=o.id,
                )
                for o in other
                if o.id not in value_ids
            )
        else:
            if value != other:
                changes.append(
                    ValueChange(
                        op=UPDATE if current else ADD,
                        element_id=incoming.id,
                        property_name=name,
                        property_value=value,
                    )
                )

    for property in incoming.umlproperties():
        property.save(incoming, save_func)

    yield from changes
