"""
With `get_icon_name` you can retrieve an icon name
for a UML model element.
"""

from gaphor import UML
import re
from functools import singledispatch


TO_KEBAB = re.compile(r"([a-z])([A-Z]+)")


def to_kebab_case(s):
    return TO_KEBAB.sub("\\1-\\2", s).lower()


@singledispatch
def get_icon_name(element):
    """
    Get an icon name for a UML model element.
    """
    return f"gaphor-{to_kebab_case(element.__class__.__name__)}-symbolic"


@get_icon_name.register(UML.Class)
def get_name_for_class(element):
    if isinstance(element, UML.Stereotype):
        return "gaphor-stereotype-symbolic"
    elif element.extension:
        return "gaphor-metaclass-symbolic"
    else:
        return "gaphor-class-symbolic"


@get_icon_name.register(UML.Property)
def get_name_for_property(element):
    if element.association:
        return "gaphor-association-symbolic"
    else:
        return "gaphor-property-symbolic"
