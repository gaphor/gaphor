"""Final state diagram item."""

from gaphor import UML
from gaphor.diagram.presentation import ElementPresentation, Named, text_name
from gaphor.diagram.shapes import Box, IconBox, ellipse, stroke
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes


@represents(UML.FinalState)
class FinalStateItem(ElementPresentation, Named):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=30, height=30)
        for h in self.handles():
            h.movable = False

        self.shape = IconBox(
            Box(draw=draw_final_state),
            text_stereotypes(self),
            text_name(self),
        )

        self.watch("subject.name")
        self.watch("subject.appliedStereotype.classifier.name")


def draw_final_state(box, context, bounding_box):
    cr = context.cairo
    r = 15

    d = r * 2
    ellipse(cr, *bounding_box)
    cr.set_line_width(0.01)
    cr.set_line_width(2)
    stroke(context, fill=True)

    if stroke_color := context.style["color"]:
        cr.set_source_rgba(*stroke_color)

    d = 20
    ellipse(cr, 5, 5, d, d)
    cr.set_line_width(0.01)
    cr.fill()
