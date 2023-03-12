from __future__ import annotations

from typing import Iterable

from gi.repository import GObject, Gio

from gaphor.core.modeling import (
    Element,
    ElementChange,
    RefChange,
    ValueChange,
    PendingChange,
)
from gaphor.i18n import gettext
from gaphor.core.changeset.apply import applicable


# TODO: add attribute changes as part of the element create operation!


class Node(GObject.Object):
    def __init__(self, element: Element | None, label: str, children: list[Node]):
        super().__init__()
        self.element = element
        self.label = label
        self.children = as_list_store(children) if children else None
        self.sync()

    label = GObject.Property(type=str, default="")
    applied = GObject.Property(type=bool, default=True)
    applicable = GObject.Property(type=bool, default=True)

    def sync(self) -> None:
        element = self.element
        if not isinstance(element, PendingChange):
            return
        self.applicable = not element.applied and applicable(element, element.model)
        self.applied = bool(element.applied)

        if self.children:
            for child in self.children:
                child.sync()


def as_list_store(list) -> Gio.ListStore:
    if isinstance(list, Gio.ListStore):
        return list

    store = Gio.ListStore.new(Node.__gtype__)
    for n in list:
        store.append(n)
    return store


def organize_changes(element_factory):
    # TODO: Iterate all diagrams / Presentations in diagram (ownedPresentation refs) / Subjects (refs to elements) / ...
    # diagram / Presentation / model elements + refs to other Presentations
    for change in element_factory.select(ElementChange):
        if change.element_name != "Diagram":
            continue
        yield from _element_changes(element_factory, "ownedPresentation")


def _element_changes(element_factory, property_name: str):
    added_removed_ids = set()

    for change in element_factory.select(ElementChange):
        if change.element_name != "Diagram":
            continue

        node = _element_change(change, element_factory, property_name)
        added_removed_ids.add(node.element.element_id)
        yield node

    for change in element_factory.select(
        lambda e: isinstance(e, RefChange)
        and e.property_name == property_name
        and e.element_id not in added_removed_ids
    ):
        element = element_factory.lookup(change.element_id)
        yield Node(
            None,
            gettext("Update element {name}").format(name=element.name)
            if hasattr(element, "name")
            else gettext("Update element of type {type}").format(
                type=type(element).__name__
            ),
            [
                *_value_changes(change.element_id, element_factory),
                *_ref_changes(change.element_id, change.op, element_factory, None),
            ],
        )


def _element_change(change, element_factory, property_name):
    if change.op == "add":
        return Node(
            change,
            gettext("Add element of type {type}").format(type=change.element_name),
            [
                *_value_changes(change.element_id, element_factory),
                *_ref_changes(
                    change.element_id, change.op, element_factory, property_name
                ),
            ],
        )
    elif change.op == "remove":
        element = element_factory.lookup(change.element_id)
        return Node(
            change,
            gettext("Remove element {name}").format(name=element.name)
            if hasattr(element, "name")
            else gettext("Remove element of type {type}").format(
                type=type(element).__name__
            ),
            [
                *_value_changes(change.element_id, element_factory),
                *_ref_changes(
                    change.element_id, change.op, element_factory, property_name
                ),
            ],
        )
    else:
        raise ValueError(f"Unknown operation for {change}: {change.op}")


def _value_changes(element_id, element_factory) -> Iterable[Node]:
    return (
        Node(
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


def _ref_changes(element_id, op, element_factory, property_name) -> Iterable[Node]:
    for rc in element_factory.select(
        lambda e: isinstance(e, RefChange)
        and e.element_id == element_id
        and e.property_name == property_name
    ):
        if element_change := next(
            element_factory.select(
                lambda e: isinstance(e, ElementChange)
                and e.element_id == rc.property_ref
            ),
            None,
        ):
            yield _element_change(element_change, element_factory, None)
        else:
            yield Node(
                rc,
                (
                    gettext("Add relation {name} to {ref_name}")
                    if op == "add"
                    else gettext("Remove relation {name} to {ref_name}")
                    if op == "remove"
                    else gettext("Update relation {name} to {ref_name}")
                ).format(
                    name=rc.property_name,
                    ref_name=_resolve_ref(rc.property_ref, element_factory),
                ),
                [],
            )


def _resolve_ref(ref, element_factory):
    element = element_factory.lookup(ref)
    if element and hasattr(element, "name"):
        return element.name
    if value_changed := next(
        element_factory.select(
            lambda e: isinstance(e, ValueChange)
            and e.element_id == ref
            and e.property_name == "name"
        ),
        None,
    ):
        return value_changed.property_value
    return gettext("nameless object")
