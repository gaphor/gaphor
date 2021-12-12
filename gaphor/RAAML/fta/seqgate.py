"""SEQ gate item definition."""

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
from gaphor.RAAML.fta.andgate import draw_and_gate
from gaphor.RAAML.fta.constants import DEFAULT_FTA_MAJOR, DEFAULT_FTA_MINOR
from gaphor.UML.recipes import stereotypes_str


@represents(raaml.SEQ)
class SEQItem(ElementPresentation, Classified):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=DEFAULT_FTA_MINOR, height=DEFAULT_FTA_MAJOR)

        self.watch("subject[NamedElement].name").watch(
            "subject[NamedElement].namespace.name"
        )

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_seq_gate,
            ),
            Text(
                text=lambda: stereotypes_str(
                    self.subject, [gettext("Sequence Enforcing Gate")]
                ),
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
    stroke(context)
