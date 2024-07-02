from __future__ import annotations

from itertools import groupby
from typing import Iterable, Sequence

from gi.repository import Gio, GObject

from gaphor.core.changeset.apply import applicable
from gaphor.core.modeling import (
    Diagram,
    ElementChange,
    PendingChange,
    Presentation,
    RefChange,
    ValueChange,
)
from gaphor.i18n import gettext


class Node(GObject.Object):
    def __init__(self, elements: list[PendingChange], children: list[Node], label: str):
        super().__init__()
        self.elements = elements
        self.label = label
        self.children: Sequence[Node] = as_list_store(children) if children else None
        self.sync()

    label = GObject.Property(type=str, default="")
    applied = GObject.Property(type=bool, default=True)
    sensitive = GObject.Property(type=bool, default=True)
    inconsistent = GObject.Property(type=bool, default=False)

    def sync(self) -> None:
        if self.children:
            for child in self.children:
                child.sync()

        self.applied = all(e.applied for e in self.elements) and (
            not self.children or all(c.applied for c in self.children)
        )
        self.sensitive = (
            not self.applied
            or any(not e.applied and applicable(e, e.model) for e in self.elements)
            or (self.children and any(c.sensitive for c in self.children))
        )
        self.inconsistent = (
            not self.applied
            and self.children
            and (
                any(c.inconsistent for c in self.children)
                or not (
                    all(c.applied for c in self.children)
                    or all(not c.applied for c in self.children)
                )
            )
        )

    def __repr__(self):
        return f"<Node elements={self.elements} label='{self.label}'>"


def as_list_store(list) -> Gio.ListStore:
    if isinstance(list, Gio.ListStore):
        return list

    store = Gio.ListStore.new(Node.__gtype__)
    for n in list:
        store.append(n)
    return store


def organize_changes(element_factory, modeling_language):
    def lookup_element(element_id: str):
        if element := element_factory.lookup(element_id):
            return type(element)
        elif element_change := next(
            element_factory.select(
                lambda e: isinstance(e, ElementChange) and e.element_id == element_id
            ),
            None,
        ):
            element_type = modeling_language.lookup_element(element_change.element_name)
            assert element_type
            return element_type
        return None

    def composite(change: RefChange):
        element_type = lookup_element(change.element_id)
        if not element_type:
            return False
        prop = getattr(element_type, change.property_name, None)
        return prop and prop.composite

    def not_presentation(change: RefChange):
        element_type = lookup_element(change.property_ref)
        return element_type and not issubclass(element_type, (Diagram, Presentation))

    def composite_and_not_presentation(change: RefChange):
        return composite(change) and not_presentation(change)

    nesting_rules = (
        composite,
        not_presentation,
        composite_and_not_presentation,
    )

    seen_change_ids: set[str] = set()

    # Add/remove diagrams
    for change in element_factory.select(
        lambda e: isinstance(e, ElementChange) and e.element_name == "Diagram"
    ):
        node = _element_change_node(change, element_factory, *nesting_rules)
        seen_change_ids.update(_all_change_ids(node))
        yield node

    # Add/remove/update presentations to existing diagrams
    for diagram in element_factory.select(
        lambda e: isinstance(e, Diagram) and e.id not in seen_change_ids
    ):
        value_changes: list[PendingChange] = list(
            _value_changes(diagram.id, element_factory)
        )
        ref_changes = list(
            _ref_change_nodes(diagram.id, element_factory, *nesting_rules)
        )
        presentation_updates = list(
            _presentation_updates(diagram, element_factory, *nesting_rules[1:])
        )
        if value_changes or ref_changes:
            node = Node(
                value_changes,
                ref_changes + presentation_updates,
                gettext("Update diagram “{name}”").format(
                    name=diagram.name or gettext("<None>")
                ),
            )
            seen_change_ids.update(_all_change_ids(node))
            yield node

    # Add/remove/update elements with/without a presentation
    for element_id, changes_iter in groupby(
        element_factory.select(
            lambda e: isinstance(e, PendingChange) and e.id not in seen_change_ids
        ),
        lambda e: e.element_id,
    ):
        changes = list(changes_iter)
        if element_change := next(
            (c for c in changes if isinstance(c, ElementChange)), None
        ):
            node = _element_change_node(
                element_change, element_factory, composite_and_not_presentation
            )
            seen_change_ids.update(_all_change_ids(node))
            yield node
        elif element := element_factory.lookup(element_id):
            node = Node(
                [c for c in changes if isinstance(c, ValueChange)],
                list(
                    _ref_change_nodes(
                        element.id, element_factory, composite_and_not_presentation
                    )
                ),
                gettext("Update element “{name}”").format(
                    name=element.name or gettext("<None>")
                )
                if element.name
                else gettext("Update element of type “{type}”").format(
                    type=type(element).__name__
                ),
            )
            seen_change_ids.update(_all_change_ids(node))
            yield node


def _all_change_ids(node: Node):
    yield from (e.id for e in node.elements)
    yield from (e.element_id for e in node.elements)
    if node.children:
        for c in node.children:
            yield from _all_change_ids(c)


def _element_change_node(change, element_factory, *nesting_rules):
    if change.op == "add":
        return Node(
            [change, *_value_changes(change.element_id, element_factory)],
            list(
                _ref_change_nodes(change.element_id, element_factory, *nesting_rules),
            ),
            _create_label(change, element_factory),
        )
    elif change.op == "remove":
        return Node(
            [*_value_changes(change.element_id, element_factory), change],
            list(
                _ref_change_nodes(change.element_id, element_factory, *nesting_rules),
            ),
            _create_label(change, element_factory),
        )
    else:
        raise ValueError(f"Unknown operation for {change}: {change.op}")


def _value_changes(element_id, element_factory) -> Iterable[ValueChange]:
    return element_factory.select(  # type: ignore[no-any-return]
        lambda e: isinstance(e, ValueChange) and e.element_id == element_id
    )


def _ref_change_nodes(
    element_id, element_factory, nesting_rule, *nesting_rules
) -> Iterable[Node]:
    for change in element_factory.select(
        lambda e: isinstance(e, RefChange) and e.element_id == element_id
    ):
        if nesting_rule(change) and (
            element_change := next(
                element_factory.select(
                    lambda e: isinstance(e, ElementChange)
                    and e.element_id == change.property_ref  # noqa: B023
                ),
                None,
            )
        ):
            yield _element_change_node(
                element_change, element_factory, *(nesting_rules or [nesting_rule])
            )
        yield Node([change], [], _create_label(change, element_factory))


def _presentation_updates(diagram, element_factory, *nesting_rules):
    for presentation in diagram.ownedPresentation:
        value_changes: list[PendingChange] = list(
            _value_changes(presentation.id, element_factory)
        )
        ref_changes = list(
            _ref_change_nodes(presentation.id, element_factory, *nesting_rules)
        )
        if value_changes or ref_changes:
            yield Node(
                value_changes,
                ref_changes,
                gettext("Update presentation “{type}”").format(type=type(presentation)),
            )


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
        if op == "add":
            return gettext("Add presentation of type {type}").format(
                type=change.element_name
            )
        if op == "remove":
            return gettext("Remove presentation of type {type}").format(
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
