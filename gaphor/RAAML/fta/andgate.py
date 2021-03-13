"""AND gate item definition."""

from math import pi

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
from gaphor.UML.modelfactory import stereotypes_str


@represents(raaml.AND)
class ANDItem(ElementPresentation, Classified):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("subject[NamedElement].name").watch(
            "subject[NamedElement].namespace.name"
        )

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: stereotypes_str(self.subject, ["AND"]),
                ),
                Text(
                    text=lambda: self.subject.name or "",
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
            draw=draw_and_gate,
        )


def draw_and_gate(box, context: DrawContext, bounding_box: Rectangle):
    cr = context.cairo
    left = bounding_box.width / 3.0
    right = bounding_box.width * 2.0 / 3.0
    shape_height = bounding_box.height - 44
    wall_top = bounding_box.height / 4.0 + 4.0
    wall_bottom = shape_height * 4.0 / 5.0 + 4.0

    # Left, bottom, right walls
    cr.move_to(left, wall_top)
    cr.line_to(left, wall_bottom)
    cr.line_to(right, wall_bottom)
    cr.line_to(right, wall_top)

    # Top arc
    rx = right - left
    ry = bounding_box.height * 2.0 / 5.0
    cr.move_to(left, wall_top)
    cr.save()
    cr.translate(left + rx / 2.0, wall_top)
    cr.scale(rx / 2.0, ry / 2.0)
    cr.arc(0.0, 0.0, 1.0, pi, 0)
    cr.restore()

    # Bottom vertical lines
    left_line = left + rx / 5.0
    cr.move_to(left_line, wall_bottom)
    cr.line_to(left_line, bounding_box.height - 40)
    right_line = right - rx / 5.0
    cr.move_to(right_line, wall_bottom)
    cr.line_to(right_line, bounding_box.height - 40)

    # Top vertical line
    center = bounding_box.width / 2.0
    cr.move_to(center, wall_top - ry / 2.0)
    cr.line_to(center, 0)
    stroke(context)
