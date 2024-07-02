"""OR gate item definition."""

from math import pi

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
from gaphor.UML.compartments import text_from_package, text_stereotypes


@represents(raaml.OR)
class ORItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=DEFAULT_FTA_MINOR, height=DEFAULT_FTA_MAJOR)

        self.watch("subject.name").watch("subject.namespace.name")

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_or_gate,
            ),
            text_stereotypes(self, lambda: [self.diagram.gettext("OR Gate")]),
            text_name(self),
            text_from_package(self),
        )


def draw_or_gate(box, context: DrawContext, bounding_box: Rectangle):
    cr = context.cairo
    left = 0
    right = bounding_box.width
    wall_top = bounding_box.height * 4.8 / 6.0
    wall_bottom = bounding_box.height * 4.5 / 5.0

    # Left wall
    cr.move_to(left, wall_bottom)
    cr.line_to(left, wall_top)

    # Right wall
    cr.move_to(right, wall_bottom)
    cr.line_to(right, wall_top)

    # Top left curve
    rx = right - left
    ry = bounding_box.height * 2.0 / 5.0
    cr.move_to(left, wall_top)
    point_top = bounding_box.height / 3.0 - ry / 2.0
    mid_width = bounding_box.width / 2.0
    cr.curve_to(
        left,
        bounding_box.height / 3.0,
        left + rx / 3.0,
        point_top,
        mid_width,
        point_top,
    )

    # Top right curve
    cr.move_to(right, wall_top)
    cr.curve_to(
        right,
        bounding_box.height / 3.0,
        right - rx / 3.0,
        point_top,
        mid_width,
        point_top,
    )

    # Bottom arc
    ry = bounding_box.height / 6.0
    cr.move_to(left, wall_bottom)
    cr.save()
    cr.translate(left + rx / 2.0, wall_bottom)
    cr.scale(rx / 2.0, ry / 2.0)
    cr.arc(0.0, 0.0, 1.0, pi, 0)
    cr.restore()

    # Bottom vertical lines
    left_line = left + rx / 5.0
    vertical_top = wall_bottom - ry / 2.4
    cr.move_to(left_line, vertical_top)
    cr.line_to(left_line, bounding_box.height)
    right_line = right - rx / 5.0
    cr.move_to(right_line, vertical_top)
    cr.line_to(right_line, bounding_box.height)

    # Top vertical line
    center = bounding_box.width / 2.0
    cr.move_to(center, point_top)
    cr.line_to(center, 0)
    stroke(context, fill=True)
