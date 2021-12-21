"""Transfer In item definition."""

from gaphas.geometry import Rectangle

from gaphor.core import gettext
from gaphor.core.modeling import DrawContext
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
)
from gaphor.diagram.shapes import Box, IconBox, Text, stroke
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontStyle, FontWeight
from gaphor.RAAML import raaml
from gaphor.RAAML.fta.constants import DEFAULT_FTA_MAJOR
from gaphor.UML.recipes import stereotypes_str


@represents(raaml.TransferIn)
class TransferInItem(ElementPresentation, Classified):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=DEFAULT_FTA_MAJOR, height=DEFAULT_FTA_MAJOR)

        self.watch("subject[NamedElement].name").watch(
            "subject[NamedElement].namespace.name"
        )

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_transfer_in,
            ),
            Text(
                text=lambda: stereotypes_str(self.subject, [gettext("Transfer In")]),
            ),
            Text(
                text=lambda: self.subject.name or "",
                width=lambda: self.width - 4,
                style={
                    "font-weight": FontWeight.BOLD,
                    "font-style": FontStyle.NORMAL,
                },
            ),
            Text(
                text=lambda: from_package_str(self),
                style={"font-size": "x-small"},
            ),
        )


def draw_transfer_in(box, context: DrawContext, bounding_box: Rectangle):
    cr = context.cairo
    cr.move_to(0, bounding_box.height)
    cr.line_to(bounding_box.width, bounding_box.height)
    cr.line_to(bounding_box.width / 2.0, 0)
    cr.line_to(0, bounding_box.height)
    stroke(context)
