"""
Artifact item
"""

from gaphor import UML
from gaphor.diagram.classifier import ClassifierItem

class ArtifactItem(ClassifierItem):

    __uml__  = UML.Artifact
    __icon__ = True

    ICON_HEIGHT = 20

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        self.height = 50
        self.width = 120
        # Set drawing style to compartment w/ small icon
        self.drawing_style = self.DRAW_COMPARTMENT_ICON
        self._line = []
        
    def update(self, context):
        super(ArtifactItem, self).update(context)
        w = self.ICON_WIDTH
        h = self.ICON_HEIGHT
        ix, iy = self.get_icon_pos()
        ear = 5
        self._line = (
                (ix + w - ear, iy + ear),
                (ix + w, iy + ear),
                (ix + w - ear, iy),
                (ix, iy),
                (ix, iy + h),
                (ix + w, iy + h),
                (ix + w, iy + ear))

    def draw_compartment_icon(self, context):
        cr = context.cairo
        cr.save()

        # draw icon
        w = self.ICON_WIDTH
        h = self.ICON_HEIGHT
        ix, iy = self.get_icon_pos()
        ear = 5
        cr.set_line_width(1.0)
        cr.move_to(ix + w - ear, iy)
        for x, y in self._line:
            cr.line_to(x, y)
        cr.stroke()

        cr.restore()
        self.draw_compartment(context)

# vim:sw=4:et
