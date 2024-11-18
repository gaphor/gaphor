"""Grouping functionality allows nesting of one item within another item
(parent item). This is useful in several use cases.

These concepts are mostly used in the ownership module (`change_owner`)
"""

from __future__ import annotations

import itertools
from collections.abc import Callable, Iterator
from enum import Enum
from functools import singledispatch

from generic.multidispatch import FunctionDispatcher, multidispatch

from gaphor.core.modeling import Base, Diagram, Presentation


def self_and_owners(element: Base | RootType | None) -> Iterator[Base]:
    """Return the element and the ancestors (Element.owner)."""
    seen = set()
    e = element
    while isinstance(e, Base):
        if e in seen:
            return
        yield e
        seen.add(e)
        e = owner(e)


def change_owner(new_parent: Base | None, element: Base) -> bool:
    if new_parent and element.model is not new_parent.model:
        return False

    o = owner(element)
    if o is Root:
        o = None

    if new_parent and o is new_parent:
        return False

    if new_parent and element in self_and_owners(new_parent):
        return False

    if new_parent is None and isinstance(o, Base):
        return ungroup(o, element)  # type: ignore[no-any-return]

    if not can_group(new_parent, element):
        return False

    if isinstance(o, Base):
        ungroup(o, element)

    return group(new_parent, element)  # type: ignore[no-any-return]


class RootType(Enum):
    Root = 1


Root = RootType.Root


@singledispatch
def owner(_element: Base) -> Base | RootType | None:
    return None


@owner.register
def _(element: Presentation):
    return element.diagram


@singledispatch
def owns(_element: Base) -> list[Base]:
    return []


@owns.register
def _(element: Diagram):
    return element.ownedPresentation


def no_group(parent, element) -> bool:
    return False


group: FunctionDispatcher[Callable[[Base, Base], bool]] = multidispatch(object, object)(
    no_group
)

group.register(None, object)(no_group)


def can_group(parent: Base | None, element_or_type: Base | type[Base]) -> bool:
    element_type = (
        type(element_or_type) if isinstance(element_or_type, Base) else element_or_type
    )
    parent_mro = type(parent).__mro__ if parent else [None]
    get_registration = group.registry.get_registration
    for t1, t2 in itertools.product(parent_mro, element_type.__mro__):
        if r := get_registration(t1, t2):
            return r is not no_group
    return False


@multidispatch(object, object)
def ungroup(parent, element) -> bool:
    return False


@ungroup.register(None, Base)
def none_ungroup(none, element):
    """In the rare (error?) case a model element has no parent, but is grouped
    in a diagram, allow it to ungroup."""
    return True
