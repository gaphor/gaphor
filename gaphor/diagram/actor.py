"""
Actor diagram item classes.
"""

from math import pi

from gaphor import UML
#from gaphor.diagram.align import V_ALIGN_BOTTOM
from gaphor.diagram.classifier import ClassifierItem

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

#    DEFAULT_SIZE= {
#        'height'     : (HEAD + NECK + BODY + ARM),
#        'width'      : (ARM * 2),
#        'min_height' : (HEAD + NECK + BODY + ARM),
#        'min_width'  : (ARM * 2)
#    }

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)

        self.drawing_style = self.DRAW_ICON

        self.min_height = self.HEAD + self.NECK + self.BODY + self.ARM
        self.min_width = self.ARM * 2
        self.height = self.min_height
        self.width = self.min_width

    def draw_icon(self, context):
        """Actors use Icon style.
        """
        c = context.cairo

        head, neck, arm, body = self.HEAD, self.NECK, self.ARM, self.BODY

        fx = self.width / (arm * 2);
        fy = self.height / (head + neck + body + arm)

        x = arm * fx
        y = (head / 2) * fy
        cy = head * fy

        c.move_to(x + head * fy / 2.0, y)
        c.arc(x, y, head * fy / 2.0, 0, 2*pi)
        #c.stroke()

        c.move_to(x, y + cy / 2)
        c.line_to(arm * fx, (head + neck + body) * fy)

        c.move_to(0, (head + neck) * fy)
        c.line_to(arm * 2 * fx, (head + neck) * fy)

        c.move_to(0, (head + neck + body + arm) * fy)
        c.line_to(arm * fx, (head + neck + body) * fy)
        c.line_to(arm * 2 * fx, (head + neck + body + arm) * fy)
        c.stroke()

        # The item's boundings are not related to the size of the actors name
        # So the update is trivial:
        text = self.subject.name
        if text:
            x_bear, y_bear, w, h, x_adv, y_adv = c.text_extents(text)
            x = 0.5 - (w / 2 + x_bear)
            y = 0.5 - (h + y_bear)
            c.move_to(self.width / 2.0 + x, self.height + h * 1.5)
            c.show_text(text)


# vim:sw=4:et
