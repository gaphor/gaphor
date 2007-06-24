"""
This module describes the interfaces specific to the gaphor.diagram module.
These interfaces are:

 - IConnect
   Use to define adapters for connecting 
 - IEditor
   Text editor interface

"""


from zope import interface


class IEditor(interface.Interface):
    """
    Provide an interface for editing text with the TextEditTool.
    """

    def is_editable(self, x, y):
        """
        Is this item editable in it's current state.
        x, y represent the cursors (x, y) position.
        (this method should be called before get_text() is called.
        """

    def get_text(self):
        """
        Get the text to be updated
        """

    def get_bounds(self):
        """
        Get the bounding box of the (current) text. The edit tool is not
        required to do anything with this information but it might help for
        some nicer displaying of the text widget.

        Returns: a gaphas.geometry.Rectangle
        """

    def update_text(self, text):
        """
        Update with the new text.
        """

    def key_pressed(self, pos, key):
        """
        Called every time a key is pressed. Allows for 'Enter' as escape
        character in single line editing.
        """

class IConnect(interface.Interface):
    """
    This interface is used by the HandleTool to allow connecting
    lines to element items. For each specific case (Element, Line) an
    adapter could be written.
    """

    def connect(self, handle, x, y):
        """
        Connect a line's handle to element.
        x and y are translated to the element the handle is connecting to.

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

    def connect_constraint(self, handle, x, y):
        """
        Connect a handle to the element.
        """

    def disconnect_constraints(self, handle):
        """
        Disconnect a line's handle from an element.
        This is called whenever a handle is dragged.
        """

    def glue(self, handle, x, y):
        """
        Determine if a handle can glue to a specific element.

        Returns a tuple (x, y) if the line and element may connect, None
        otherwise.
        """


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
