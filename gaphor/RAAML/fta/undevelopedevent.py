"""Undeveloped Event item definition."""

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
from gaphor.RAAML.fta.constants import WIDE_FTA_HEIGHT, WIDE_FTA_WIDTH
from gaphor.UML.recipes import stereotypes_str


@represents(raaml.Undeveloped)
class UndevelopedEventItem(ElementPresentation, Classified):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=WIDE_FTA_WIDTH, height=WIDE_FTA_HEIGHT)

        self.watch("subject[NamedElement].name").watch(
            "subject[NamedElement].namespace.name"
        )

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_undeveloped_event,
            ),
            Text(
                text=lambda: stereotypes_str(
                    self.subject, [gettext("Undeveloped Event")]
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


def draw_undeveloped_event(box, context: DrawContext, bounding_box: Rectangle):
    x1 = 0
    x2 = bounding_box.width
    y1 = 0
    y2 = bounding_box.height
    draw_diamond(context, x1, x2, y1, y2)
