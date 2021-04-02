"""Containment - A relationship that makes an item an ownedElement of another."""

from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.shapes import draw_crossed_circle_head


class ContainmentItem(LinePresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)
        self.draw_tail = draw_crossed_circle_head
