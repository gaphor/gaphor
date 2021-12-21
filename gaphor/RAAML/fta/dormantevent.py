"""Dormant Event item definition."""

from gaphas.geometry import Rectangle

from gaphor.core import gettext
from gaphor.core.modeling import DrawContext
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
)
from gaphor.diagram.shapes import Box, IconBox, Text, draw_diamond
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontStyle, FontWeight
from gaphor.RAAML import raaml
from gaphor.RAAML.fta.undevelopedevent import draw_undeveloped_event
from gaphor.UML.recipes import stereotypes_str


@represents(raaml.DormantEvent)
class DormantEventItem(ElementPresentation, Classified):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=70, height=35)

        self.watch("subject[NamedElement].name").watch(
            "subject[NamedElement].namespace.name"
        )

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_dormant_event,
            ),
            Text(
                text=lambda: stereotypes_str(self.subject, [gettext("Dormant Event")]),
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


def draw_dormant_event(box, context: DrawContext, bounding_box: Rectangle):
    draw_undeveloped_event(box, context, bounding_box)
    x1 = bounding_box.width / 5.0
    x2 = bounding_box.width * 4.0 / 5.0
    y1 = bounding_box.height / 5.0
    y2 = bounding_box.height * 4.0 / 5.0
    draw_diamond(context, x1, x2, y1, y2)
