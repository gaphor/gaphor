from __future__ import annotations

from typing import NamedTuple

from gaphor.core.modeling import (
    Element,
    ElementChange,
    RefChange,
    ValueChange,
    PendingChange,
)
from gaphor.i18n import gettext


class Item(NamedTuple):
    element: Element | None
    text: str
    children: list[Item]


def organize_changes(element_factory):
    for change in element_factory.select(ElementChange):
        if change.op == "add":
            yield Item(
                change,
                gettext("Add element of type {type}").format(type=change.element_name),
                [
                    *_value_changes(change.element_id, element_factory),
                    *_ref_changes(change.element_id, change.op, element_factory),
                ],
            )
        elif change.op == "remove":
            element = element_factory.lookup(change.element_id)
            yield Item(
                change,
                gettext("Remove element {name}").format(name=element.name),
                [
                    *_value_changes(change.element_id, element_factory),
                    *_ref_changes(change.element_id, change.op, element_factory),
                ],
            )

    added_removed = {c.element_id for c in element_factory.select(ElementChange)}

    for change in element_factory.select(PendingChange):
        if change.element_id in added_removed:
            continue
        element = element_factory.lookup(change.element_id)
        yield Item(
            None,
            gettext("Update element {name}").format(name=element.name)
            if hasattr(element, "name")
            else gettext("Update element of type {type}").format(
                type=type(element).__name__
            ),
            [
                *_value_changes(change.element_id, element_factory),
                *_ref_changes(change.element_id, change.op, element_factory),
            ],
        )


def _value_changes(element_id, element_factory):
    return (
        Item(
            vc,
            "Update attribute {name} to {value}".format(
                name=vc.property_name, value=vc.property_value
            ),
            [],
        )
        for vc in element_factory.select(
            lambda e: isinstance(e, ValueChange) and e.element_id == element_id
        )
    )


def _ref_changes(element_id, op, element_factory):
    return (
        Item(
            vc,
            (
                gettext("Add relation {name} to {ref_name}")
                if op == "add"
                else gettext("Remove relation {name} to {ref_name}")
                if op == "remove"
                else gettext("Update relation {name} to {ref_name}")
            ).format(
                name=vc.property_name,
                ref_name=_resolve_ref(vc.property_ref, element_factory),
            ),
            [],
        )
        for vc in element_factory.select(
            lambda e: isinstance(e, RefChange) and e.element_id == element_id
        )
    )


def _resolve_ref(ref, element_factory):
    element = element_factory.lookup(ref)
    if element and hasattr(element, "name"):
        return element.name
    if name := next(
        element_factory.select(
            lambda e: isinstance(e, ValueChange) and e.property_name == "name"
        ),
        None,
    ):
        return name
    return gettext("<None>")
