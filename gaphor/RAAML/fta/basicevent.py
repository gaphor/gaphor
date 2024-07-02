"""Basic Event item definition."""

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    text_name,
)
from gaphor.diagram.shapes import Box, IconBox, ellipse, stroke
from gaphor.diagram.support import represents
from gaphor.RAAML import raaml
from gaphor.RAAML.fta.constants import DEFAULT_FTA_MAJOR
from gaphor.UML.compartments import text_from_package, text_stereotypes


@represents(raaml.BasicEvent)
class BasicEventItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=DEFAULT_FTA_MAJOR, height=DEFAULT_FTA_MAJOR)

        self.watch("subject.name").watch("subject.namespace.name")

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_basic_event,
            ),
            text_stereotypes(self, lambda: [self.diagram.gettext("Basic Event")]),
            text_name(self),
            text_from_package(self),
        )


def draw_basic_event(box, context: DrawContext, bounding_box: Rectangle):
    cr = context.cairo
    cr.move_to(bounding_box.width, bounding_box.height)
    ellipse(cr, *bounding_box)
    stroke(context, fill=True)
