'''
Use case diagram item
'''
# vim:sw=4

from math import pi
from gaphor import UML
from gaphor.diagram.classifier import ClassifierItem
from gaphas.util import text_align, text_extents, path_ellipse

class UseCaseItem(ClassifierItem):
    """Presentation of gaphor.UML.UseCase.
    """
    __uml__ = UML.UseCase

    def __init__(self, id):
        ClassifierItem.__init__(self, id, 50, 30)
        self.drawing_style = -1

    def pre_update(self, context):
        cr = context.cairo
        text = self.subject.name
        if text:
            width, height = text_extents(cr, text)
            self.min_width, self.min_height = width + 10, height + 20
        super(UseCaseItem, self).pre_update(context)

    def draw(self, context):
        c = context.cairo

        rx = self.width / 2. 
        ry = self.height / 2.

        c.move_to(self.width, ry)
        path_ellipse(c, rx, ry, self.width, self.height)
        c.stroke()

        text = self.subject.name
        if text:
            text_align(c, rx, ry, text, align_x=0)


# vim:sw=4:et
