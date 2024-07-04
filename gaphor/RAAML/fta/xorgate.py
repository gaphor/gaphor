"""XOR gate item definition."""

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
from gaphor.RAAML.fta.constants import DEFAULT_FTA_MAJOR, DEFAULT_FTA_MINOR
from gaphor.RAAML.fta.orgate import draw_or_gate
from gaphor.UML.compartments import text_from_package, text_stereotypes


@represents(raaml.XOR)
class XORItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=DEFAULT_FTA_MINOR, height=DEFAULT_FTA_MAJOR)

        self.watch("subject.name").watch("subject.namespace.name")

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_xor_gate,
            ),
            text_stereotypes(self, lambda: [self.diagram.gettext("XOR Gate")]),
            text_name(self),
            text_from_package(self),
        )


def draw_xor_gate(box, context: DrawContext, bounding_box: Rectangle):
    draw_or_gate(box, context, bounding_box)
    cr = context.cairo
    wall_bottom = bounding_box.height * 4.0 / 5.0
    ry = bounding_box.height * 2.0 / 5.0
    point_top = bounding_box.height / 3.0 - ry / 2.0

    # Triangle
    bottom_points = wall_bottom + bounding_box.height / 12.0
    cr.move_to(0, bottom_points)
    cr.line_to(bounding_box.width / 2.0, point_top)
    cr.line_to(bounding_box.width, bottom_points)
    stroke(context, fill=True)
