from __future__ import annotations

from typing import Iterable

from gaphor.core.changeset.apply import ADD, REMOVE, UPDATE
from gaphor.core.modeling import (
    Element,
    ElementChange,
    ElementFactory,
    RefChange,
    ValueChange,
)
from gaphor.core.modeling.collection import collection


class UnmatchableModel(Exception):
    def __init__(self, current, incoming):
        super().__init__(f"Incompatible types {current} != {incoming}")
        self.current = current
        self.incoming = incoming


def compare(
    current: ElementFactory, incoming: ElementFactory
) -> Iterable[ElementChange | ValueChange | RefChange]:
    """Compare two models.

    Changes are recorded in the current model as `PendingChange` objects
    (`ElementChange`, `ValueChange`, `RefChange`). Returns an iterable
    of the added change objects
    """
    current_keys = set(current.keys())
    incoming_keys = set(incoming.keys())

    def create(type, **kwargs):
        e = current.create(type)
        for name, value in kwargs.items():
            setattr(e, name, value)
        return e

    for key in current_keys.difference(incoming_keys):
        e = current[key]
        yield create(
            ElementChange,
            op=REMOVE,
            element_name=type(e).__name__,
            element_id=key,
        )

    for key in incoming_keys.difference(current_keys):
        e = incoming[key]
        yield create(
            ElementChange,
            op=ADD,
            element_name=type(e).__name__,
            element_id=key,
        )
        yield from updated_properties(None, e, create)

    for key in current_keys.intersection(incoming_keys):
        c = current[key]
        i = incoming[key]
        if type(c) is not type(i):
            raise UnmatchableModel(c, i)
        yield from updated_properties(c, i, create)


def updated_properties(current, incoming, create):
    changes: list[ValueChange | RefChange] = []

    def save_func(name, value):
        other = getattr(current, name) if current else None
        if isinstance(value, Element):
            # Allow values to be None
            if (value and value.id) != (other and other.id):
                changes.append(
                    create(
                        RefChange,
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
                create(
                    RefChange,
                    op=ADD,
                    element_id=incoming.id,
                    property_name=name,
                    property_ref=v.id,
                )
                for v in value
                if v.id not in other_ids
            )
            changes.extend(
                create(
                    RefChange,
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
                    create(
                        ValueChange,
                        op=UPDATE if current else ADD,
                        element_id=incoming.id,
                        property_name=name,
                        property_value=value,
                    )
                )

    for property in incoming.umlproperties():
        property.save(incoming, save_func)

    yield from changes
