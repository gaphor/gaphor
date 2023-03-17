from __future__ import annotations

from typing import Iterable, Sequence

from gi.repository import GObject, Gio

from gaphor.core.modeling import (
    ElementChange,
    RefChange,
    ValueChange,
    PendingChange,
)
from gaphor.i18n import gettext
from gaphor.core.changeset.apply import applicable
from gaphor.core.modeling import Diagram


class Node(GObject.Object):
    def __init__(self, elements: list[PendingChange], children: list[Node], label: str):
        super().__init__()
        self.elements = elements
        self.label = label
        self.children: Sequence[Node] = as_list_store(children) if children else None
        self.sync()

    label = GObject.Property(type=str, default="")
    applied = GObject.Property(type=bool, default=True)
    applicable = GObject.Property(type=bool, default=True)

    def sync(self) -> None:
        self.applicable = any(
            not e.applied and applicable(e, e.model) for e in self.elements
        )
        self.applied = all(e.applied for e in self.elements)

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
    def _not_presentation(change):
        if element := element_factory.lookup(change.property_ref):
            name = type(element).__name__
        if element_change := next(
            element_factory.select(
                lambda e: isinstance(e, ElementChange)
                and e.element_id == change.property_ref
            ),
            None,
        ):
            name = element_change.element_name
        return name and not (name == "Diagram" or name.endswith("Item"))

    property_names = (
        lambda change: change.property_name == "ownedPresentation",
        _not_presentation,
        lambda _: False,
    )

    seen_change_ids: set[str] = set()

    for change in element_factory.select(
        lambda e: isinstance(e, ElementChange) and e.element_name == "Diagram"
    ):
        node = _element_change(change, element_factory, *property_names)
        seen_change_ids.update(_all_change_ids(node))
        yield node

    # TODO: Add/remove/update presentations to existing diagrams
    for diagram in element_factory.select(Diagram):
        value_changes: list[PendingChange] = [
            val
            for val in _value_changes(diagram.id, element_factory)
            if val.id not in seen_change_ids
        ]
        ref_changes = [
            ref
            for ref in _ref_changes(diagram.id, element_factory, *property_names)
            if all(e.id not in seen_change_ids for e in ref.elements)
        ]
        if value_changes or ref_changes:
            node = Node(
                value_changes,
                ref_changes,
                gettext("Update diagram “{name}”").format(
                    name=diagram.name or gettext("<None>")
                ),
            )
            seen_change_ids.update(_all_change_ids(node))
            yield node

        # TODO: check updates for ownedPresentation

    # TODO: Add/remove/update elements with/without a presentation


def _all_change_ids(node: Node):
    yield from (e.id for e in node.elements)
    if node.children:
        for c in node.children:
            yield from _all_change_ids(c)


def _element_change(change, element_factory, *property_names):
    if change.op == "add":
        return Node(
            [change, *_value_changes(change.element_id, element_factory)],
            list(
                _ref_changes(change.element_id, element_factory, *property_names),
            ),
            _create_label(change, element_factory),
        )
    elif change.op == "remove":
        return Node(
            [*_value_changes(change.element_id, element_factory), change],
            list(
                _ref_changes(change.element_id, element_factory, *property_names),
            ),
            _create_label(change, element_factory),
        )
    else:
        raise ValueError(f"Unknown operation for {change}: {change.op}")


def _value_changes(element_id, element_factory) -> Iterable[ValueChange]:
    return element_factory.select(  # type: ignore[no-any-return]
        lambda e: isinstance(e, ValueChange) and e.element_id == element_id
    )


def _ref_changes(
    element_id, element_factory, property_name, *nested_properties
) -> Iterable[Node]:
    for change in element_factory.select(
        lambda e: isinstance(e, RefChange) and e.element_id == element_id
    ):
        if (
            property_name(change)
            and nested_properties
            and (
                element_change := next(
                    element_factory.select(
                        lambda e: isinstance(e, ElementChange)
                        and e.element_id == change.property_ref
                    ),
                    None,
                )
            )
        ):
            yield _element_change(element_change, element_factory, *nested_properties)
        else:
            yield Node([change], [], _create_label(change, element_factory))


def _create_label(change, element_factory):
    element = element_factory.lookup(change.element_id)
    name = (
        element.name
        if hasattr(element, "name")
        else v.property_value
        if (
            v := next(
                element_factory.select(
                    lambda e: isinstance(e, ValueChange)
                    and e.element_id == change.element_id
                    and e.property_name == "name"
                ),
                None,
            )
        )
        else None
    )

    op = change.op
    if isinstance(change, ElementChange) and change.element_name.endswith("Item"):
        # TODO: find subject type
        if op == "add":
            return gettext("Add presentation of type {type}").format(
                type=change.element_name
            )
        elif op == "remove":
            return gettext("Add presentation of type {type}").format(
                type=change.element_name
            )
        else:
            return (
                gettext("Update presentation “{name}”").format(name=name)
                if name
                else gettext("Update presentation of type {type}").format(
                    type=type(element).__name__
                )
            )
    if isinstance(change, ElementChange):
        if op == "add":
            return (
                gettext("Add {type} “{name}”").format(
                    type=change.element_name, name=name
                )
                if name
                else gettext("Add element of type {type}").format(
                    type=change.element_name
                )
            )
        elif op == "remove":
            return (
                gettext("Remove element “{name}”").format(name=name)
                if name
                else gettext("Remove element of type {type}").format(
                    type=type(element).__name__
                )
            )
        else:
            return (
                gettext("Update element “{name}”").format(name=name)
                if name
                else gettext("Update element of type {type}").format(
                    type=type(element).__name__
                )
            )
    elif isinstance(change, RefChange):
        if ref_name := _resolve_ref(change.property_ref, element_factory):
            return (
                gettext("Add relation “{name}” to “{ref_name}”")
                if op == "add"
                else gettext("Remove relation “{name}” to “{ref_name}”")
                if op == "remove"
                else gettext("Update relation “{name}” to “{ref_name}”")
            ).format(
                name=change.property_name,
                ref_name=ref_name,
            )
        else:
            return (
                gettext("Add relation “{name}”")
                if op == "add"
                else gettext("Remove relation “{name}”")
                if op == "remove"
                else gettext("Update relation “{name}”")
            ).format(
                name=change.property_name,
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
    return None
