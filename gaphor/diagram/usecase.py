'''
Use case diagram item
'''
# vim:sw=4

from math import pi
from gaphor import UML
from gaphor.diagram.classifier import ClassifierItem
from gaphas.util import text_center, path_ellipse

class UseCaseItem(ClassifierItem):
    """Presentation of gaphor.UML.UseCase.
    """
    __uml__      = UML.UseCase

    def __init__(self, id):
        ClassifierItem.__init__(self, id)
        self.min_width = 50
        self.min_height = 30
        self.width = self.min_width
        self.height = self.min_height

    def update(self, context):
        c = context.cairo
        text = self.subject.name
        if text:
            _, _, self.min_width, self.min_height, _, _ = c.text_extents(text)
        ClassifierItem.update(self, context)

    def draw(self, context):
        c = context.cairo

        rx = self.width / 2. 
        ry = self.height / 2.

        c.move_to(self.width, ry)
        path_ellipse(c, rx, ry, self.width, self.height)
        c.stroke()

        text = self.subject.name
        if text:
            text_center(c, rx, ry, text)


# vim:sw=4:et
