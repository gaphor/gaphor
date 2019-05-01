"""
This module describes the interfaces specific to the gaphor.diagram module.
These interfaces are:

 - IConnect
   Use to define adapters for connecting
 - IEditor
   Text editor interface

"""

from zope import interface

from functools import singledispatch


@singledispatch
def IEditor(obj):
    pass


class IConnect(interface.Interface):
    """
    This interface is used by the HandleTool to allow connecting
    lines to element items. For each specific case (Element, Line) an
    adapter could be written.
    """

    def connect(self, handle, port):
        """
        Connect a line's handle to element.

        Note that at the moment of the connect, handle.connected_to may point
        to some other item. The implementor should do the disconnect of
        the other element themselves.
        """

    def disconnect(self, handle):
        """
        The true disconnect. Disconnect a handle.connected_to from an
        element. This requires that the relationship is also removed at
        model level.
        """

    def connect_constraints(self, handle):
        """
        Connect a handle to the element.
        """

    def disconnect_constraints(self, handle):
        """
        Disconnect a line's handle from an element.
        This is called whenever a handle is dragged.
        """

    def glue(self, handle):
        """
        Determine if a handle can glue to a specific element.

        Returns a tuple (x, y) if the line and element may connect, None
        otherwise.
        """


# TODO: I think this should have been called Namespacing or something similar,
# since that's the modeling concept.
class IGroup(interface.Interface):
    """
    Provide interface for adding one UML object to another, i.e.
    interactions contain lifelines and components contain classes objects.
    """

    def pre_can_contain(self):
        """
        Determine if parent can contain item, which is instance of given
        class. Method called before item creation.
        """

    def can_contain(self):
        """
        Determine if parent can contain item.
        """

    def group(self):
        """
        Perform grouping of items.
        """

    def ungroup(self):
        """
        Perform ungrouping of items.
        """


# vim: sw=4:et:ai
