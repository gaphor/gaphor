from functools import singledispatch

from gaphor.core.modeling import Element, Presentation


@singledispatch
def deletable(element: Element) -> bool:
    """Determine if a single element can safely be deleted."""
    return True


@singledispatch
def item_explicitly_deletable(item: Presentation):
    return True
