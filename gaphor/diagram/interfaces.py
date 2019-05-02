"""
This module describes the interfaces specific to the gaphor.diagram module.
These interfaces are:

 - IConnect
   Use to define adapters for connecting
 - Editor
   Text editor interface

"""

from zope import interface

from functools import singledispatch


@singledispatch
def Editor(obj):
    pass


class IConnect(interface.Interface):
    """
    This interface is used by the HandleTool to allow connecting
    lines to element items. For each specific case (Element, Line) an
    adapter could be written.
    """

    pass


# TODO: I think this should have been called Namespacing or something similar,
# since that's the modeling concept.
class IGroup(interface.Interface):
    """
    Provide interface for adding one UML object to another, i.e.
    interactions contain lifelines and components contain classes objects.
    """

    pass


# vim: sw=4:et:ai
