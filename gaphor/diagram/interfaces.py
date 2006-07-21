"""
This module describes the interfaces specific to the gaphor.diagram module.
These interfaces are:

 - IConnectable
   Use to define adapters for connecting 
 - IEditor
   Text editor interface

"""


from zope import interface


class IDiagramItem(interface.Interface):
    """A diagram element"""
    subject = interface.Attribute("The model element connect to this view")    

class ICommentItem(IDiagramItem):
    """A view on a Comment item."""

class INamedItem(IDiagramItem):
    """A view on an attribute (part of a class, interface etc.)."""
    

class IClassItem(INamedItem):
    """The graphical view on a class."""
    

class IAttributeItem(INamedItem):
    """A view on an attribute (part of a class, interface etc.)."""


class IEditor(interface.Interface):
    """Provide an interface for editing text. with the TextEditTool.
    """

    def is_editable(self, x, y):
        """Is this item editable in it's current state.
        x, y represent the cursors (x, y) position.
        """

    def get_text(self):
        """Get the text to be updated
        """

    def get_bounds(self):
        """Get the bounding box of the (current) text. The edit tool is not
        required to do anything with this information but it might help for
        some nicer displaying of the text widget.

        Returns: a gaphas.geometry.Rectangle
        """

    def update_text(self, text):
        """Update with the new text.
        """

    def key_pressed(self, pos, key):
        """Called every time a key is pressed. Allows for 'Enter' as escape
        character in single line editing.
        """

# vim: sw=4:et:ai
