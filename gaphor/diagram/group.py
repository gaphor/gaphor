"""Grouping functionality allows nesting of one item within another item
(parent item). This is useful in several use cases.

- artifact deployed within a node
- a class within a package, or a component
- composite structures (i.e. component within a node)
"""

from __future__ import annotations

import itertools
from typing import Callable

from generic.multidispatch import FunctionDispatcher, multidispatch

from gaphor.core.modeling import Diagram, Element, self_and_owners


def change_owner(new_parent, element):
    if new_parent and element.model is not new_parent.model:
        return False

    if new_parent and element.owner is new_parent:
        return False

    if new_parent and element in self_and_owners(new_parent):
        return False

    if new_parent is None and element.owner:
        return ungroup(element.owner, element)

    if not can_group(new_parent, element):
        return False

    if element.owner:
        ungroup(element.owner, element)

    return group(new_parent, element)


def no_group(parent, element) -> bool:
    return False


class GroupPreconditions:
    def __init__(self, func):
        self.__func = func

    def __getattr__(self, key):
        return getattr(self.__func, key)

    def __call__(self, parent, element) -> bool:
        if element in self_and_owners(parent):
            return False

        return self.__func(parent, element)  # type: ignore[no-any-return]


group: FunctionDispatcher[Callable[[Element, Element], bool]] = GroupPreconditions(
    multidispatch(object, object)(no_group)
)
group.register(None, object)(no_group)


def can_group(parent: Element, element_or_type: Element | type[Element]) -> bool:
    element_type = (
        type(element_or_type)
        if isinstance(element_or_type, Element)
        else element_or_type
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


@ungroup.register(None, Element)
def none_ungroup(none, element):
    """In the rare (error?) case a model element has no parent, but is grouped
    in a diagram, allow it to ungroup."""
    return True


@group.register(Element, Diagram)
def diagram_group(element, diagram):
    diagram.element = element
    return True


@ungroup.register(Element, Diagram)
def diagram_ungroup(element, diagram):
    if diagram.element is element:
        del diagram.element
        return True
    return False
