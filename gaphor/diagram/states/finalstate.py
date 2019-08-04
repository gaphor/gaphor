"""
Final state diagram item.
"""

from gaphor import UML
from gaphor.UML.modelfactory import stereotypes_str
from gaphas.util import path_ellipse
from gaphor.diagram.states.state import VertexItem
from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.shapes import Box, IconBox, EditableText, Text
from gaphor.diagram.text import TextAlign, VerticalAlign
from gaphor.diagram.support import represents


@represents(UML.FinalState)
class FinalStateItem(ElementPresentation, VertexItem):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        for h in self.handles():
            h.movable = False

        self.shape = IconBox(
            Box(draw=draw_final_state),
            Text(
                text=lambda: stereotypes_str(self.subject),
                style={"min-width": 0, "min-height": 0},
            ),
            EditableText(text=lambda: self.subject and self.subject.name or ""),
        )

        self.watch("subject<NamedElement>.name")
        self.watch("subject.appliedStereotype.classifier.name")


def draw_final_state(box, context, bounding_box):
    cr = context.cairo
    r = 16
    d = 20
    path_ellipse(cr, r, r, d, d)
    cr.set_line_width(0.01)
    cr.fill()

    d = r * 2
    path_ellipse(cr, r, r, d, d)
    cr.set_line_width(0.01)
    cr.set_line_width(2)
    cr.stroke()
