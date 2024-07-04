"""Transfer Out item definition."""

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    text_name,
)
from gaphor.diagram.shapes import Box, IconBox, stroke
from gaphor.diagram.support import represents
from gaphor.RAAML import raaml
from gaphor.RAAML.fta.constants import DEFAULT_FTA_MAJOR
from gaphor.RAAML.fta.transferin import draw_transfer_in
from gaphor.UML.compartments import text_from_package, text_stereotypes


@represents(raaml.TransferOut)
class TransferOutItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=DEFAULT_FTA_MAJOR, height=DEFAULT_FTA_MAJOR)

        self.watch("subject.name").watch("subject.namespace.name")

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_transfer_out,
            ),
            text_stereotypes(self, lambda: [self.diagram.gettext("Transfer Out")]),
            text_name(self),
            text_from_package(self),
        )


def draw_transfer_out(box, context: DrawContext, bounding_box: Rectangle):
    draw_transfer_in(box, context, bounding_box)
    cr = context.cairo
    cr.move_to(bounding_box.width / 4.0, bounding_box.height / 2.0)
    cr.line_to(0, bounding_box.height / 2.0)
    stroke(context, fill=True)
