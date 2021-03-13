"""Dormant Event item definition."""

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext
from gaphor.core.styling import VerticalAlign
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
)
from gaphor.diagram.shapes import Box, Text, draw_diamond
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontStyle, FontWeight
from gaphor.RAAML import raaml
from gaphor.RAAML.fta.undevelopedevent import draw_undeveloped_event
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
            draw=draw_dormant_event,
        )


def draw_dormant_event(box, context: DrawContext, bounding_box: Rectangle):
    draw_undeveloped_event(box, context, bounding_box)
    x1 = bounding_box.width / 3.0
    x2 = bounding_box.width * 2.0 / 3.0
    y1 = bounding_box.height / 8.0
    y2 = bounding_box.height * 7.0 / 8.0 - 46
    draw_diamond(context, x1, x2, y1, y2)
