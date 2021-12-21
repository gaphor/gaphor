"""Pseudostate diagram items.

See also gaphor.UML.states package description.
"""

from gaphas.item import SE
from gaphas.util import path_ellipse

from gaphor import UML
from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.shapes import Box, IconBox, Text, stroke
from gaphor.diagram.support import represents
from gaphor.UML.recipes import stereotypes_str
from gaphor.UML.states.state import VertexItem


@represents(UML.Pseudostate)
class PseudostateItem(ElementPresentation, VertexItem):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=20, height=20)
        for h in self.handles():
            h.movable = False

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject[Pseudostate].kind", self.update_shapes)

    def update_shapes(self, event=None):
        if self.subject and self.subject.kind == "shallowHistory":
            box = Box(draw=draw_history_pseudostate)
            self.handles()[SE].pos = (30, 30)
        else:
            box = Box(draw=draw_initial_pseudostate)
            self.handles()[SE].pos = (20, 20)

        self.shape = IconBox(
            box,
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(text=lambda: self.subject.name or ""),
        )


def draw_initial_pseudostate(box, context, bounding_box):
    """Draw initial pseudostate symbol."""
    cr = context.cairo
    stroke = context.style["color"]
    if stroke:
        cr.set_source_rgba(*stroke)
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
    stroke(context)

    cr.move_to(12, 10)
    cr.line_to(12, 20)
    cr.move_to(18, 10)
    cr.line_to(18, 20)
    cr.move_to(12, 15)
    cr.line_to(18, 15)
    stroke(context, fill=False)
