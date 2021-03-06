"""Inhibit gate item definition."""

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext
from gaphor.core.styling import VerticalAlign
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
)
from gaphor.diagram.shapes import Box, EditableText, Text, stroke
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontStyle, FontWeight
from gaphor.RAAML import raaml
from gaphor.UML.modelfactory import stereotypes_str


@represents(raaml.INHIBIT)
class InhibitItem(ElementPresentation, Classified):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("subject[NamedElement].name").watch(
            "subject[NamedElement].namespace.name"
        )

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: stereotypes_str(self.subject, ["INHIBIT"]),
                ),
                EditableText(
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
            draw=draw_inhibit_gate,
        )


def draw_inhibit_gate(box, context: DrawContext, bounding_box: Rectangle):
    cr = context.cairo

    # Top vertical line
    left = bounding_box.width / 4.0
    middle_width = left + bounding_box.width * 2.0 / 10.0
    cr.move_to(middle_width, 4)
    shape_height = bounding_box.height - 44
    top_point = shape_height / 7.0 + 4.0
    cr.line_to(middle_width, top_point)

    # Move around the hexagon counter-clockwise
    upper = shape_height / 3.0 + 4.0
    cr.line_to(left, upper)  # 1st side
    lower = shape_height * 2.0 / 3.0 + 4.0
    cr.line_to(left, lower)  # 2nd side
    bottom_point = shape_height * 5.0 / 6.0 + 4
    cr.line_to(middle_width, bottom_point)  # 3rd side
    right = left + bounding_box.width * 4 / 10.0
    cr.line_to(right, lower)  # 4th side
    cr.line_to(right, upper)  # 5th side
    cr.line_to(middle_width, top_point)  # 6th side

    # Bottom vertical line
    cr.move_to(middle_width, shape_height + 4)
    cr.line_to(middle_width, bottom_point)

    # Right horizontal line
    middle_height = shape_height / 2.0 + 4.0
    cr.move_to(right, middle_height)
    cr.line_to(left + bounding_box.width / 2.0, middle_height)
    stroke(context)
