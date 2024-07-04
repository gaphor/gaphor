"""Inhibit gate item definition."""

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
from gaphor.UML.compartments import text_from_package, text_stereotypes


@represents(raaml.INHIBIT)
class InhibitItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=DEFAULT_FTA_MAJOR, height=DEFAULT_FTA_MAJOR)

        self.watch("subject.name").watch("subject.namespace.name")

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_inhibit_gate,
            ),
            text_stereotypes(self, lambda: [self.diagram.gettext("Inhibit Gate")]),
            text_name(self),
            text_from_package(self),
        )


def draw_inhibit_gate(box, context: DrawContext, bounding_box: Rectangle):
    cr = context.cairo

    # Top vertical line
    left = 0
    middle_width = bounding_box.width * 5.0 / 12.0
    bottom_point = bounding_box.height * 5.0 / 6.0
    top_point = bounding_box.height / 6.0
    right = bounding_box.width * 5.0 / 6.0
    upper = bounding_box.height / 3.0
    lower = bounding_box.height * 2.0 / 3.0
    cr.move_to(middle_width, 0)
    cr.line_to(middle_width, top_point)

    # Move around the hexagon counter-clockwise
    cr.line_to(left, upper)  # 1st side
    cr.line_to(left, lower)  # 2nd side
    cr.line_to(middle_width, bottom_point)  # 3rd side
    cr.line_to(right, lower)  # 4th side
    cr.line_to(right, upper)  # 5th side
    cr.line_to(middle_width, top_point)  # 6th side

    # Bottom vertical line
    cr.move_to(middle_width, bounding_box.height)
    cr.line_to(middle_width, bottom_point)

    # Right horizontal line
    middle_height = bounding_box.height / 2.0
    cr.move_to(right, middle_height)
    cr.line_to(bounding_box.width, middle_height)
    stroke(context, fill=True)
