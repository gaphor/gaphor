"""XOR gate item definition."""

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext
from gaphor.core.styling import VerticalAlign
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
)
from gaphor.diagram.shapes import Box, Text, stroke
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontStyle, FontWeight
from gaphor.RAAML import raaml
from gaphor.RAAML.fta.orgate import draw_or_gate
from gaphor.UML.modelfactory import stereotypes_str


@represents(raaml.XOR)
class XORItem(ElementPresentation, Classified):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("subject[NamedElement].name").watch(
            "subject[NamedElement].namespace.name"
        )

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: stereotypes_str(self.subject, ["XOR"]),
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
                style={
                    "padding": (55, 4, 0, 4),
                    "min-height": 100,
                },
            ),
            style={"vertical-align": VerticalAlign.BOTTOM},
            draw=draw_xor_gate,
        )


def draw_xor_gate(box, context: DrawContext, bounding_box: Rectangle):
    draw_or_gate(box, context, bounding_box)
    cr = context.cairo
    left = bounding_box.width / 3.0
    right = bounding_box.width * 2.0 / 3.0
    shape_height = bounding_box.height - 44
    wall_top = bounding_box.height / 4.0 + 4.0
    wall_bottom = shape_height * 4.0 / 5.0 + 4.0

    # Triangle
    cr.move_to(left, wall_bottom)
    ry = bounding_box.height * 2.0 / 5.0
    cr.line_to(bounding_box.width / 2.0, wall_top - ry / 2.0)
    cr.line_to(right, wall_bottom)
    stroke(context)
