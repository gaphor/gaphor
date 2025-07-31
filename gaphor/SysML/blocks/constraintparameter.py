"""Constraint Parameter item."""

from dataclasses import replace

from gaphor import UML
from gaphor.core.styling import TextAlign, VerticalAlign
from gaphor.diagram.presentation import AttachedPresentation, Named
from gaphor.diagram.shapes import (
    Box,
    IconBox,
    Text,
    draw_border,
)
from gaphor.UML.umlfmt import format_property


class StyleInjector:
    """A shape that injects style properties."""

    def __init__(self, child, **style):
        self.child = child
        self.style = style

    def size(self, context, bounding_box=None):
        style = {**context.style, **self.style}
        return self.child.size(replace(context, style=style), bounding_box)

    def draw(self, context, bounding_box):
        style = {**context.style, **self.style}
        self.child.draw(replace(context, style=style), bounding_box)

    def __iter__(self):
        return iter((self.child,))


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
        side = self.connected_side
        spacing = 5  # Adjustable offset in pixels

        if side == "left":
            # Position text block to the RIGHT, but justify text lines to the LEFT
            icon_box_style = {
                "text-align": TextAlign.RIGHT,
                "vertical-align": VerticalAlign.MIDDLE,
                "vertical-spacing": spacing,
            }
            text_style = {"text-align": TextAlign.LEFT}
        elif side == "right":
            # Position text block to the LEFT, but justify text lines to the RIGHT
            icon_box_style = {
                "text-align": TextAlign.LEFT,
                "vertical-align": VerticalAlign.MIDDLE,
                "vertical-spacing": spacing,
            }
            text_style = {"text-align": TextAlign.RIGHT}
        elif side == "top":
            # Position text block BELOW, and justify text lines to the CENTER
            icon_box_style = {
                "text-align": TextAlign.CENTER,
                "vertical-align": VerticalAlign.BOTTOM,
                "vertical-spacing": spacing,
            }
            text_style = {"text-align": TextAlign.CENTER}
        elif side == "bottom":
            # Position text block ABOVE, and justify text lines to the CENTER
            icon_box_style = {
                "text-align": TextAlign.CENTER,
                "vertical-align": VerticalAlign.TOP,
                "vertical-spacing": spacing,
            }
            text_style = {"text-align": TextAlign.CENTER}
        else:
            # Default position when not connected
            icon_box_style = {
                "text-align": TextAlign.CENTER,
                "vertical-align": VerticalAlign.BOTTOM,
                "vertical-spacing": spacing,
            }
            text_style = {"text-align": TextAlign.CENTER}

        shape = IconBox(
            Box(draw=draw_border),
            StyleInjector(
                Text(
                    text=lambda: format_property(
                        self.subject, type=True, multiplicity=True
                    )
                    or ""
                ),
                **text_style,
            ),
        )
        self.shape = StyleInjector(shape, **icon_box_style)

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

    def unlink(self) -> None:
        """
        On deletion, we want to keep the underlying `UML.Property`.
        It is owned by the `Constraint` and should not be deleted with its
        presentation.
        """
        self.subject = None
        super().unlink()

    def disconnect(self, handle):
        """
        Disconnect from the parent item.
        """
        if self.parent:
            self.diagram.connections.disconnect_item(self, handle)
            self.parent = None
