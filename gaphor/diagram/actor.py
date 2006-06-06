"""
Actor diagram item classes.
"""

import diacanvas

from gaphor import UML
from gaphor.diagram.align import V_ALIGN_BOTTOM
from gaphor.diagram.classifier import ClassifierItem

class ActorItem(ClassifierItem):
    """
    Actor item is a classifier in icon mode. In future maybe it will be
    possible to switch to comparment mode.
    """

    __uml__      = UML.Actor
    __o_align__  = True
    __s_valign__ = V_ALIGN_BOTTOM

    HEAD = 11
    ARM  = 19
    NECK = 10
    BODY = 20

    DEFAULT_SIZE= {
        'height'     : (HEAD + NECK + BODY + ARM),
        'width'      : (ARM * 2),
        'min_height' : (HEAD + NECK + BODY + ARM),
        'min_width'  : (ARM * 2)
    }

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)

        self.drawing_style = self.DRAW_ICON

        self.set(**self.DEFAULT_SIZE)

        # Head
        self._head = diacanvas.shape.Ellipse()
        self._head.set_line_width(2.0)
        # Body
        self._body = diacanvas.shape.Path()
        self._body.set_line_width(2.0)
        # Arm
        self._arms = diacanvas.shape.Path()
        self._arms.set_line_width(2.0)
        # Legs
        self._legs = diacanvas.shape.Path()
        self._legs.set_line_width(2.0)

        self._shapes.update((self._head, self._body,
            self._arms, self._legs))


    def draw_border(self):
        pass


    def update_icon(self, affine):
        """Actors use Icon style, so update it.
        """
        fx = self.width / (self.ARM * 2);
        fy = self.height / (self.HEAD + self.NECK + self.BODY + self.ARM)

        x = self.ARM * fx
        y = (self.HEAD / 2) * fy
        r1 = self.HEAD * fx
        r2 = self.HEAD * fy
        self._head.ellipse((x, y), r1, r2)

        self._body.line(((x, y + r2 / 2),
            (self.ARM * fx,
            (self.HEAD + self.NECK + self.BODY) * fy)))

        self._arms.line(((0, (self.HEAD + self.NECK) * fy),
            (self.ARM * 2 * fx,
            (self.HEAD + self.NECK) * fy)))

        self._legs.line(((0, (self.HEAD + self.NECK + self.BODY + self.ARM) * fy),
            (self.ARM * fx, (self.HEAD + self.NECK + self.BODY) * fy),
            (self.ARM * 2 * fx, (self.HEAD + self.NECK + self.BODY + self.ARM) * fy)))

# vim:sw=4
