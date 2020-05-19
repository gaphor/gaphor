"""
Pseudostate diagram items.

See also gaphor.UML.states package description.
"""

from gaphas.util import path_ellipse

from gaphor import UML
from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.shapes import Box, EditableText, IconBox, Text
from gaphor.diagram.support import represents
from gaphor.UML.modelfactory import stereotypes_str
from gaphor.UML.states.state import VertexItem


@represents(UML.Pseudostate)
class PseudostateItem(ElementPresentation, VertexItem):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        for h in self.handles():
            h.movable = False

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject[Pseudostate].kind", self.update_shapes)

    def update_shapes(self):
        self.shape = IconBox(
            Box(
                draw=draw_history_pseudostate
                if self.subject and self.subject.kind == "shallowHistory"
                else draw_initial_pseudostate
            ),
            Text(text=lambda: stereotypes_str(self.subject),),
            EditableText(text=lambda: self.subject.name or ""),
        )


def draw_initial_pseudostate(box, context, bounding_box):
    """
    Draw initial pseudostate symbol.
    """
    cr = context.cairo
    r = 10
    d = r * 2
    path_ellipse(cr, r, r, d, d)
    cr.set_line_width(0.01)
    cr.fill()


def draw_history_pseudostate(box, context, bounding_box):
    cr = context.cairo
    r = 15
    d = r * 2
    path_ellipse(cr, r, r, d, d)
    # cr.set_line_width(1)
    cr.move_to(12, 10)
    cr.line_to(12, 20)
    cr.move_to(18, 10)
    cr.line_to(18, 20)
    cr.move_to(12, 15)
    cr.line_to(18, 15)
    cr.stroke()
