"""Final state diagram item."""

from gaphas.util import path_ellipse

from gaphor import UML
from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.shapes import Box, IconBox, Text, stroke
from gaphor.diagram.support import represents
from gaphor.UML.recipes import stereotypes_str
from gaphor.UML.states.state import VertexItem


@represents(UML.FinalState)
class FinalStateItem(VertexItem, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=30, height=30)
        for h in self.handles():
            h.movable = False

        self.shape = IconBox(
            Box(draw=draw_final_state),
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(text=lambda: self.subject and self.subject.name or ""),
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")


def draw_final_state(box, context, bounding_box):
    cr = context.cairo
    r = 15

    d = r * 2
    path_ellipse(cr, r, r, d, d)
    cr.set_line_width(0.01)
    cr.set_line_width(2)
    stroke(context)

    if stroke_color := context.style["color"]:
        cr.set_source_rgba(*stroke_color)

    d = 20
    path_ellipse(cr, r, r, d, d)
    cr.set_line_width(0.01)
    cr.fill()
