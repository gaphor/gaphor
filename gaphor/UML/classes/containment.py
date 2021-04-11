"""Containment - A relationship that makes an item an ownedElement of another."""

from gaphor.core.modeling import DrawContext
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.shapes import pi, stroke


class ContainmentItem(LinePresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)
        self.draw_head = draw_crossed_circle_head


def draw_crossed_circle_head(context: DrawContext):
    cr = context.cairo
    radius = 7
    cr.save()
    cr.move_to(0, 0)
    cr.set_dash((), 0)
    cr.arc(radius, 0.0, radius, 0.0, 2 * pi)
    cr.move_to(0, 0)
    cr.line_to(2 * radius, 0)
    cr.move_to(radius, radius)
    cr.line_to(radius, -radius)
    stroke(context, dash=False)
    cr.restore()
    cr.move_to(0, 0)
