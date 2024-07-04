"""Pseudostate diagram items.

See also gaphor.UML.states package description.
"""

from gaphas.item import SE

from gaphor import UML
from gaphor.core.modeling.properties import relation_one
from gaphor.diagram.presentation import ElementPresentation, Named, text_name
from gaphor.diagram.shapes import Box, IconBox, ellipse, stroke
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes


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
        super().__init__(diagram, id, width=6, height=20)
        for h in self.handles():
            h.movable = False

        self.watch("subject.name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject[Pseudostate].kind", self.update_shapes)

    def update_shapes(self, event=None):
        kind = self.subject.kind if self.subject and self.subject.kind else "initial"
        draw, width, height = PSEUDOSTATE_SHAPE[kind]
        self.handles()[SE].pos = (width, height)

        self.shape = IconBox(
            Box(draw=draw),
            text_stereotypes(self),
            text_name(self),
        )


def draw_initial_or_junction_pseudostate(box, context, bounding_box):
    """Draw initial pseudostate symbol."""
    cr = context.cairo
    if stroke := context.style["color"]:
        cr.set_source_rgba(*stroke)
    ellipse(cr, *bounding_box)
    cr.set_line_width(0.01)
    cr.fill()


def draw_deep_history_pseudostate(box, context, bounding_box):
    cr = context.cairo
    ellipse(cr, *bounding_box)
    cr.move_to(9, 10)
    cr.line_to(9, 20)
    cr.move_to(15, 10)
    cr.line_to(15, 20)
    cr.move_to(9, 15)
    cr.line_to(15, 15)

    for p in ((21, 9), (25, 12), (18.5, 17), (23.5, 17), (17, 12)):
        cr.move_to(21, 13)
        cr.line_to(*p)
    stroke(context, fill=False)


def draw_shallow_history_pseudostate(box, context, bounding_box):
    cr = context.cairo
    ellipse(cr, *bounding_box)
    cr.move_to(12, 10)
    cr.line_to(12, 20)
    cr.move_to(18, 10)
    cr.line_to(18, 20)
    cr.move_to(12, 15)
    cr.line_to(18, 15)
    stroke(context, fill=False)


def draw_join_or_fork_pseudostate(box, context, bounding_box):
    cr = context.cairo
    if stroke := context.style.get("color"):
        cr.set_source_rgba(*stroke)

    cr.set_line_width(6)
    cr.move_to(3, 0)
    cr.line_to(3, 40)
    cr.stroke()


def draw_choice_pseudostate(box, context, bounding_box):
    cr = context.cairo
    cr.move_to(15, 0)
    cr.line_to(30, 15)
    cr.line_to(15, 30)
    cr.line_to(0, 15)
    cr.close_path()
    stroke(context, fill=False)


def draw_entry_point_pseudostate(box, context, bounding_box):
    ellipse(context.cairo, *bounding_box)


def draw_exit_point_pseudostate(box, context, bounding_box):
    cr = context.cairo
    ellipse(cr, *bounding_box)
    cr.move_to(5, 5)
    cr.line_to(25, 25)
    cr.move_to(5, 25)
    cr.line_to(25, 5)
    stroke(context, fill=False)


def draw_terminate_pseudostate(box, context, bounding_box):
    cr = context.cairo
    cr.move_to(0, 0)
    cr.line_to(30, 20)
    cr.move_to(0, 20)
    cr.line_to(30, 0)
    stroke(context, fill=False)


PSEUDOSTATE_SHAPE = {
    "initial": (draw_initial_or_junction_pseudostate, 20, 20),
    "deepHistory": (draw_deep_history_pseudostate, 30, 30),
    "shallowHistory": (draw_shallow_history_pseudostate, 30, 30),
    "join": (draw_join_or_fork_pseudostate, 6, 40),
    "fork": (draw_join_or_fork_pseudostate, 6, 40),
    "junction": (draw_initial_or_junction_pseudostate, 20, 20),
    "choice": (draw_choice_pseudostate, 30, 30),
    "entryPoint": (draw_entry_point_pseudostate, 30, 30),
    "exitPoint": (draw_exit_point_pseudostate, 30, 30),
    "terminate": (draw_terminate_pseudostate, 30, 20),
}
