from __future__ import annotations

from operator import setitem
from typing import Iterable

from gaphor.core.modeling import (
    Element,
    ElementChange,
    ElementFactory,
    RefChange,
    ValueChange,
    Presentation,
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
    (`ElementChange`, `ValueChange`, `RefChange`).

    Returns an iterable of the added change objects.
    """
    current_keys = set(current.keys())
    incoming_keys = set(incoming.keys())

    def create(type, **kwargs):
        e = current.create(type)
        for name, value in kwargs.items():
            setattr(e, name, None if value is None else str(value))
        return e

    for key in current_keys.difference(incoming_keys):
        e = current[key]
        yield create(
            ElementChange,
            op="remove",
            element_name=type(e).__name__,
            element_id=key,
        )

    for key in incoming_keys.difference(current_keys):
        e = incoming[key]
        yield create(
            ElementChange,
            op="add",
            element_name=type(e).__name__,
            element_id=key,
            diagram_id=e.diagram.id if isinstance(e, Presentation) else None,
        )
        yield from updated_properties(None, e, create)

    for key in current_keys.intersection(incoming_keys):
        c = current[key]
        i = incoming[key]
        if type(c) is not type(i):
            raise UnmatchableModel(c, i)
        yield from updated_properties(c, i, create)


def updated_properties(current, incoming, create) -> Iterable[ValueChange | RefChange]:
    current_vals: dict[str, Element | collection[Element] | str | int | None] = {}
    if current:
        current.save(lambda n, v: setitem(current_vals, n, v))
    incoming_vals: dict[str, Element | collection[Element] | str | int | None] = {}
    incoming.save(lambda n, v: setitem(incoming_vals, n, v))

    for name in {*current_vals.keys(), *incoming_vals.keys()}:
        value = incoming_vals.get(name)
        other = current_vals.get(name)
        if isinstance(value, Element):
            # Allow values to be None
            assert other is None or isinstance(other, Element)
            if other is None or value.id != other.id:
                yield create(
                    RefChange,
                    op="update",
                    element_id=incoming.id,
                    property_name=name,
                    property_ref=value.id,
                )
        elif isinstance(value, collection):
            assert other is None or isinstance(other, collection)
            other_ids = {o.id for o in other} if other is not None else set()

            yield from (
                create(
                    RefChange,
                    op="add",
                    element_id=incoming.id,
                    property_name=name,
                    property_ref=v.id,
                )
                for v in value
                if v.id not in other_ids
            )
        elif value != other:
            if isinstance(other, Element):
                yield create(
                    RefChange,
                    op="update",
                    element_id=incoming.id,
                    property_name=name,
                    property_ref=None,
                )
            elif not isinstance(other, collection):
                yield create(
                    ValueChange,
                    op="update",
                    element_id=incoming.id,
                    property_name=name,
                    property_value=value,
                )

        if isinstance(other, collection):
            assert value is None or isinstance(value, collection)
            value_ids = {v.id for v in value} if value else set()

            yield from (
                create(
                    RefChange,
                    op="remove",
                    element_id=incoming.id,
                    property_name=name,
                    property_ref=o.id,
                )
                for o in other
                if o.id not in value_ids
            )
