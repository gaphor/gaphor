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
