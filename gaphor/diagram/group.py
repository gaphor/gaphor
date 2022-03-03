"""Grouping functionality allows nesting of one item within another item
(parent item). This is useful in several use cases.

- artifact deployed within a node
- a class within a package, or a component
- composite structures (i.e. component within a node)
"""

from __future__ import annotations

from generic.multidispatch import multidispatch


@multidispatch(object, object)
def group(parent, element) -> bool:
    return False


@multidispatch(object, object)
def ungroup(parent, element) -> bool:
    return False
