'''
Use case diagram item
'''
# vim:sw=4

from math import pi
from gaphor import UML
from gaphor.diagram.classifier import ClassifierItem

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

        h0 = self.handles()[0]
        rx = self.width / 2. 
        ry = self.height / 2.

        c.translate(h0.x, h0.y)
        c.move_to(self.width, ry)
        path_ellipse(c, rx, ry, self.width, self.height)
        c.stroke()

        text = self.subject.name
        if text:
            text_center(c, rx, ry, text)


def text_center(cr, x, y, text):
    """Draw text using (x, y) as center.
    x    - center x
    y    - center y
    text - text to print (utf8)
    """
    x_bear, y_bear, w, h, x_adv, y_adv = cr.text_extents(text)
    x = 0.5 - (w / 2 + x_bear) + x
    y = 0.5 - (h / 2 + y_bear) + y
    cr.move_to(x, y)
    cr.show_text(text)


def path_ellipse (cr, x, y, width, height, angle=0):
    """Draw an ellipse.
    x      - center x
    y      - center y
    width  - width of ellipse  (in x direction when angle=0)
    height - height of ellipse (in y direction when angle=0)
    angle  - angle in radians to rotate, clockwise
    """
    cr.save()
    cr.translate (x, y)
    cr.rotate (angle)
    cr.scale (width / 2.0, height / 2.0)
    cr.arc (0.0, 0.0, 1.0, 0.0, 2.0 * pi)
    cr.restore()


# vim:sw=4:et
