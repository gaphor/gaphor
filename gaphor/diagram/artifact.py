'''
ArtifactItem diagram item
'''
# vim:sw=4:et

from __future__ import generators

import gobject
import pango
import diacanvas
from gaphor import UML
from classifier import ClassifierItem

class ArtifactItem(ClassifierItem):

    __uml__ = UML.Artifact

    ICON_HEIGHT = 20

#    popup_menu = ClassifierItem.popup_menu \
#        + ('separator', 'IndirectlyInstantiated')

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        self.set(height=50, width=120)
        # Set drawing style to compartment w/ small icon
        self.drawing_style = self.DRAW_COMPARTMENT_ICON
        # TODO: underline text
        
        for attr in ('_note',):
            shape = diacanvas.shape.Path()
            shape.set_line_width(1.0)
            shape.set_fill(True)
            shape.set_fill_color(diacanvas.color(255, 255, 255))
            setattr(self, attr, shape)

    def update_compartment_icon(self, affine):

        ClassifierItem.update_compartment_icon(self, affine)

        # draw icon
        w = self.ICON_WIDTH
        h = self.ICON_HEIGHT
        ix = self.width - self.ICON_MARGIN_X - self.ICON_WIDTH
        iy = self.ICON_MARGIN_Y
        ear = 5

        self._note.line(((ix + w - ear, iy), (ix + w - ear, iy + ear),
                         (ix + w, iy + ear), (ix + w - ear, iy),
                         (ix, iy), (ix, iy + h), (ix + w, iy + h),
                         (ix + w, iy + ear)))

    def on_shape_iter(self):
        for s in ClassifierItem.on_shape_iter(self):
            yield s
        yield self._note
