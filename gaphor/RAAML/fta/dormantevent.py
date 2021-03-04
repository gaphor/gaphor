"""Dormant Event item definition."""

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


@represents(raaml.DormantEvent)
class DormantEventItem(ElementPresentation, Classified):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("subject[NamedElement].name").watch(
            "subject[NamedElement].namespace.name"
        )

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: stereotypes_str(self.subject, ["DormantEvent"]),
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
            draw=draw_dormant_event,
        )


def draw_dormant_event(box, context: DrawContext, bounding_box: Rectangle):
    cr = context.cairo

    # Outer diamond
    outer_x1 = bounding_box.width / 4.0
    outer_x2 = bounding_box.width * 3.0 / 4.0
    center_x = bounding_box.width / 2.0
    center_y = bounding_box.height / 2.0 - 25.0
    outer_y1 = 4
    outer_y2 = bounding_box.height - 50
    cr.move_to(outer_x1, center_y)
    cr.line_to(center_x, outer_y2)
    cr.line_to(outer_x2, center_y)
    cr.line_to(center_x, outer_y1)
    cr.line_to(outer_x1, center_y)

    # Inner diamond
    inner_x1 = bounding_box.width / 3.0
    inner_x2 = bounding_box.width * 2.0 / 3.0
    inner_y1 = bounding_box.height / 8.0
    inner_y2 = bounding_box.height * 7.0 / 8.0 - 46
    cr.move_to(inner_x1, center_y)
    cr.line_to(center_x, inner_y2)
    cr.line_to(inner_x2, center_y)
    cr.line_to(center_x, inner_y1)
    cr.line_to(inner_x1, center_y)

    stroke(context)
