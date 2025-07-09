"""Constraint Parameter item."""

from gaphor import UML
from gaphor.diagram.presentation import AttachedPresentation, Named
from gaphor.diagram.shapes import (
    Box,
    CssNode,
    IconBox,
    Text,
    draw_border,
)
from gaphor.UML.umlfmt import format_property


class ConstraintParameterItem(Named, AttachedPresentation[UML.Property]):
    """
    An item that represents a constraint parameter as an attached item.
    """

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=16, height=16)
        self.watch("subject[UML:NamedElement].name").watch(
            "subject[UML:TypedElement].type.name"
        ).watch("subject[Property].lowerValue").watch("subject[Property].upperValue")

        # Make the handle connectable, so the connect tool can start a connection.
        # An AttachedPresentation has one handle, which we can access at index 0.
        self.handles()[0].connectable = True

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(draw=draw_border),
            CssNode(
                "name",
                self.subject,
                Text(
                    text=lambda: format_property(
                        self.subject, type=True, multiplicity=True
                    )
                    or ""
                ),
            ),
        )

    def connect(self, handle, port):
        """
        Allow the item to be connected to a new parent, even if it already
        has one. This enables "gluing" the parameter to a different item.

        This overrides the default `AttachedPresentation.connect()` which
        prevents connecting if a parent already exists.
        """
        if not port.connectable:
            return False

        # The key change: allow re-parenting by changing the parent.
        self.parent = port.owner

        # Register the connection, which will update the existing connection if one exists.
        self.diagram.connections.connect_item(self, handle, port)
        return True

    def disconnect(self, handle):
        """
        Disconnect from the parent item.
        """
        if self.parent:
            self.diagram.connections.disconnect_item(self, handle)
            self.parent = None
