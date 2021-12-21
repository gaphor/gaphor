"""Top Event item definition."""

from gaphas.geometry import Rectangle

from gaphor.core import gettext
from gaphor.core.modeling import DrawContext
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
)
from gaphor.diagram.shapes import Box, Text, draw_border
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontStyle, FontWeight
from gaphor.RAAML import raaml
from gaphor.UML.recipes import stereotypes_str


@represents(raaml.TopEvent)
class TopEventItem(ElementPresentation, Classified):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("subject[NamedElement].name").watch(
            "subject[NamedElement].namespace.name"
        )

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: stereotypes_str(self.subject, [gettext("Top Event")]),
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
                style={"padding": (12, 4, 12, 4)},
            ),
            draw=draw_top_event,
        )


def draw_top_event(box, context: DrawContext, bounding_box: Rectangle):
    draw_border(box, context, bounding_box)
