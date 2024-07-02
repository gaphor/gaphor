"""House Event item definition."""

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


@represents(raaml.HouseEvent)
class HouseEventItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=DEFAULT_FTA_MINOR, height=DEFAULT_FTA_MAJOR)

        self.watch("subject.name").watch("subject.namespace.name")

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_house_event,
            ),
            text_stereotypes(self, lambda: [self.diagram.gettext("House Event")]),
            text_name(self),
            text_from_package(self),
        )


def draw_house_event(box, context: DrawContext, bounding_box: Rectangle):
    cr = context.cairo
    left = 0
    right = bounding_box.width
    wall_top = bounding_box.height / 3.0
    wall_bottom = bounding_box.height
    cr.move_to(left, wall_bottom)
    cr.line_to(right, wall_bottom)
    cr.line_to(right, wall_top)
    cr.line_to(bounding_box.width / 2.0, 0)
    cr.line_to(left, wall_top)
    cr.line_to(left, wall_bottom)
    stroke(context, fill=True)
