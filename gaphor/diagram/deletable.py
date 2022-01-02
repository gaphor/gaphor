from functools import singledispatch

from gaphor.core.modeling import Element


@singledispatch
def deletable(element: Element) -> bool:
    """Determine if a single element can safely be deleted."""
    return True
