"""
Actor item classes.
"""

from math import pi

from gaphas.util import text_align, text_set_font

from gaphor import UML
#from gaphor.diagram.align import V_ALIGN_BOTTOM
from gaphor.diagram.classifier import ClassifierItem
import font

class ActorItem(ClassifierItem):
    """Actor item is a classifier in icon mode.

    In future maybe it will be possible to switch to comparment mode.
    """

    __uml__ = UML.Actor
#    __o_align__  = True
#    __s_valign__ = V_ALIGN_BOTTOM

    HEAD = 11
    ARM  = 19
    NECK = 10
    BODY = 20

    def __init__(self, id = None):
        ClassifierItem.__init__(self, id)

        self.drawing_style = self.DRAW_ICON

        self.min_height = self.HEAD + self.NECK + self.BODY + self.ARM
        self.min_width = self.ARM * 2
        self.height = self.min_height
        self.width = self.min_width

    def draw_icon(self, context):
        """Actors use Icon style.
        """
        cr = context.cairo

        head, neck, arm, body = self.HEAD, self.NECK, self.ARM, self.BODY

        fx = self.width / (arm * 2);
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

        # The item's boundings are not related to the size of the actors name
        # So the update is trivial:
        text = self.subject.name
        if text:
            text_set_font(cr, font.FONT_NAME)
            text_align(cr, self.width/2.0, self.height + 10, text, align_y=0)


# vim:sw=4:et
