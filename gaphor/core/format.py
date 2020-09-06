"""
Format() and parse() provide a simple interface to:

1. format a model element to text
2. Update model element contents based on text
"""

from functools import singledispatch

from gaphor.core.modeling import Element


@singledispatch
def format(el: Element) -> str:
    """
    Format an element.
    """
    raise TypeError("Format routine for type %s not implemented yet" % type(el))


@singledispatch
def parse(el: Element, text: str) -> None:
    """
    Parse text and update `el` accordingly.
    """
    raise TypeError("Parsing routine for type %s not implemented yet" % type(el))
