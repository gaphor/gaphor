"""Pseudostate diagram items.

See also gaphor.UML.states package description.
"""

from gaphas.item import SE
from gaphas.util import path_ellipse

from gaphor import UML
from gaphor.core.modeling.properties import relation_one
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, IconBox, Text, stroke
from gaphor.diagram.support import represents
from gaphor.UML.recipes import stereotypes_str


@represents(UML.Pseudostate)
class PseudostateItem(ElementPresentation, Named):
    """A Pseudostate:

    * initial (solid circle, in: 0, out: 1)
    * deepHistory (circle with "H*", in: *, out: 1)
    * shallowHistory (circle with "H", in: *, out: 1)
    * join (bar, in: *, out: 1)
    * fork (bar, in: 1, out: *)
    * junction (solid circle, in: *, out: *)
    * choice (diamond, in: *, out: *)
    * entryPoint (circle, in: *, out: *)
    * exitPoint (circle with cross, in: *, out: *)
    * terminate (cross, in: *, out: *)
    """

    subject: relation_one[UML.Pseudostate]

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=20, height=20)
        for h in self.handles():
            h.movable = False

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject[Pseudostate].kind", self.update_shapes)

    def update_shapes(self, event=None):
        kind = self.subject.kind if self.subject and self.subject.kind else "initial"
        draw, width, height = PSEUSOSTATE_SHAPE[kind]
        self.handles()[SE].pos = (width, height)

        self.shape = IconBox(
            Box(draw=draw),
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(text=lambda: self.subject.name or ""),
        )


def draw_initial_pseudostate(box, context, bounding_box):
    """Draw initial pseudostate symbol."""
    cr = context.cairo
    if stroke := context.style["color"]:
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


PSEUSOSTATE_SHAPE = {
    "initial": (draw_initial_pseudostate, 20, 20),
    "deepHistory": (draw_history_pseudostate, 30, 30),
    "shallowHistory": (draw_history_pseudostate, 30, 30),
    "join": (draw_history_pseudostate, 30, 30),
    "fork": (draw_history_pseudostate, 30, 30),
    "junction": (draw_history_pseudostate, 30, 30),
    "choice": (draw_history_pseudostate, 30, 30),
    "entryPoint": (draw_history_pseudostate, 30, 30),
    "exitPoint": (draw_history_pseudostate, 30, 30),
    "terminate": (draw_history_pseudostate, 30, 30),
}
