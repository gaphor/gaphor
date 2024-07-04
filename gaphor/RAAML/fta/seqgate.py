"""SEQ gate item definition."""

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
from gaphor.RAAML.fta.andgate import draw_and_gate
from gaphor.RAAML.fta.constants import DEFAULT_FTA_MAJOR, DEFAULT_FTA_MINOR
from gaphor.UML.compartments import text_from_package, text_stereotypes


@represents(raaml.SEQ)
class SEQItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=DEFAULT_FTA_MINOR, height=DEFAULT_FTA_MAJOR)

        self.watch("subject.name").watch("subject.namespace.name")

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_seq_gate,
            ),
            text_stereotypes(
                self, lambda: [self.diagram.gettext("Sequence Enforcing Gate")]
            ),
            text_name(self),
            text_from_package(self),
        )


def draw_seq_gate(box, context: DrawContext, bounding_box: Rectangle):
    draw_and_gate(box, context, bounding_box)
    cr = context.cairo
    wall_top = bounding_box.height / 2.0
    wall_bottom = bounding_box.height * 4.0 / 5.0

    # Triangle
    cr.move_to(0, wall_bottom)
    ry = bounding_box.height * 2.0 / 3.0
    cr.line_to(bounding_box.width / 2.0, wall_top - ry / 2.0)
    cr.line_to(bounding_box.width, wall_bottom)
    stroke(context, fill=True)
