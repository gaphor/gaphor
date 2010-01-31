"""
Module dealing with options (typing) of icons.
"""

from gaphor import UML
from simplegeneric import generic


@generic
def get_icon_option(element):
    """
    Default behaviour: no options.
    """
    return


@get_icon_option.when_type(UML.Class)
def get_option_class(element):
    if element.extension:
        return 'metaclass'


@get_icon_option.when_type(UML.Component)
def get_option_component(element):
    for p in element.presentation:
        if hasattr(p, '__stereotype__') and p.__stereotype__ == 'subsystem':
            return 'subsystem'


@get_icon_option.when_type(UML.Property)
def get_option_property(element):
    if element.association:
        return 'association-end'

# vim:sw=4:et:ai
