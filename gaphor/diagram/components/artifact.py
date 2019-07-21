"""
Artifact item.
"""

from gaphor import UML
from gaphor.diagram.classifier import ClassifierItem


class ArtifactItem(ClassifierItem):

    __uml__ = UML.Artifact
    __icon__ = True

    __style__ = {"name-padding": (10, 25, 10, 10)}

    ICON_HEIGHT = 20

    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        self.height = 50
        self.width = 120
        # Set drawing style to compartment w/ small icon
        self.drawing_style = self.DRAW_COMPARTMENT_ICON
        self._line = []

    def pre_update_compartment_icon(self, context):
        super().pre_update_compartment_icon(context)
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
            (ix + w, iy + ear),
        )

    def draw_compartment_icon(self, context):
        cr = context.cairo
        cr.save()
        self.draw_compartment(context)
        cr.restore()

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
