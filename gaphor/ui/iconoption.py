"""
Module dealing with options (typing) of icons.
"""

from gaphor import UML
from functools import singledispatch


@singledispatch
def get_icon_option(element):
    """
    Default behaviour: no options.
    """
    return


@get_icon_option.register(UML.Class)
def get_option_class(element):
    if element.extension:
        return "metaclass"


@get_icon_option.register(UML.Component)
def get_option_component(element):
    for p in element.presentation:
        try:
            if p.__stereotype__ == "subsystem":
                return "subsystem"
        except AttributeError:
            pass


@get_icon_option.register(UML.Property)
def get_option_property(element):
    if element.association:
        return "association-end"


# vim:sw=4:et:ai
