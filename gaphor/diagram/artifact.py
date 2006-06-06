"""
Artifact item
"""

import diacanvas
from gaphor import UML
from gaphor.diagram.classifier import ClassifierItem

class ArtifactItem(ClassifierItem):

    __uml__  = UML.Artifact
    __icon__ = True

    ICON_HEIGHT = 20

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        self.set(height=50, width=120)
        # Set drawing style to compartment w/ small icon
        self.drawing_style = self.DRAW_COMPARTMENT_ICON
        # TODO: underline text
        
        self._note = diacanvas.shape.Path()
        self._note.set_line_width(1.0)
        self._note.set_fill(True)
        self._note.set_fill_color(diacanvas.color(255, 255, 255))
        self._shapes.add(self._note)


    def update_compartment_icon(self, affine):
        ClassifierItem.update_compartment_icon(self, affine)

        # draw icon
        w = self.ICON_WIDTH
        h = self.ICON_HEIGHT
        ix, iy = self.get_icon_pos()
        ear = 5

        self._note.line(((ix + w - ear, iy), (ix + w - ear, iy + ear),
                         (ix + w, iy + ear), (ix + w - ear, iy),
                         (ix, iy), (ix, iy + h), (ix + w, iy + h),
                         (ix + w, iy + ear)))


# vim:sw=4:et
