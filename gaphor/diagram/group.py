"""Grouping functionality allows nesting of one item within another item
(parent item). This is useful in several use cases.

- artifact deployed within a node
- a class within a package, or a component
- composite structures (i.e. component within a node)

The grouping adapters has to implement three methods, see `AbstractGroup`
class.

It is important to note, that grouping adapters can be queried before
instance of an item to be grouped is created. This happens when item
is about to be created. Therefore, `AbstractGroup.can_contain` has
to be aware `AbstractGroup.item` can be null.
"""

from __future__ import annotations

from generic.multidispatch import multidispatch

from gaphor.core.modeling import Element


@multidispatch(Element, Element)
def group(parent: Element | None, element: Element | None) -> bool:
    return False


def no_group(parent: Element | None, element: Element | None) -> bool:
    return False


# Until we can deal with types (esp. typing.Any) we use this as a workaround:
group.register(None, Element)(no_group)
group.register(Element, None)(no_group)
