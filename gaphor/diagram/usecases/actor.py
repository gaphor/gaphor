"""
Actor item classes.
"""

from math import pi

from gaphor import UML
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_BOTTOM
from gaphor.diagram.classifier import ClassifierItem


class ActorItem(ClassifierItem):
    """
    Actor item is a classifier in icon mode.

    Maybe it should be possible to switch to comparment mode in the future.
    """

    __uml__ = UML.Actor

    HEAD = 11
    ARM = 19
    NECK = 10
    BODY = 20
    __style__ = {
        "min-size": (ARM * 2, HEAD + NECK + BODY + ARM),
        "name-align": (ALIGN_CENTER, ALIGN_BOTTOM),
        "name-padding": (5, 0, 5, 0),
        "name-outside": True,
    }

    def __init__(self, id=None, factory=None):
        ClassifierItem.__init__(self, id, factory)

        self.drawing_style = self.DRAW_ICON

    def draw_icon(self, context):
        """
        Draw actor's icon creature.
        """
        super(ActorItem, self).draw(context)

        cr = context.cairo

        head, neck, arm, body = self.HEAD, self.NECK, self.ARM, self.BODY

        fx = self.width / (arm * 2)
        fy = self.height / (head + neck + body + arm)

        x = arm * fx
        y = (head / 2) * fy
        cy = head * fy

        cr.move_to(x + head * fy / 2.0, y)
        cr.arc(x, y, head * fy / 2.0, 0, 2 * pi)

        cr.move_to(x, y + cy / 2)
        cr.line_to(arm * fx, (head + neck + body) * fy)

        cr.move_to(0, (head + neck) * fy)
        cr.line_to(arm * 2 * fx, (head + neck) * fy)

        cr.move_to(0, (head + neck + body + arm) * fy)
        cr.line_to(arm * fx, (head + neck + body) * fy)
        cr.line_to(arm * 2 * fx, (head + neck + body + arm) * fy)
        cr.stroke()


# vim:sw=4:et
