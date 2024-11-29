from functools import singledispatch

from gaphor.core.modeling import Base


@singledispatch
def deletable(_element: Base) -> bool:
    """Determine if a single element can safely be deleted."""
    return True
