'''
NodeItem diagram item
'''
# vim:sw=4:et

from __future__ import generators

import gobject
import pango
import diacanvas
import gaphor.UML as UML
from gaphor.diagram import initialize_item
from classifier import ClassifierItem

class NodeItem(ClassifierItem):
    DEPTH = 10

#    popup_menu = ClassifierItem.popup_menu \
#        + ('separator', 'IndirectlyInstantiated')

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        self.set(height=50, width=120)
        # Set drawing style to compartment w// small icon
        #self.drawing_style = self.DRAW_COMPARTMENT_ICON

        for attr in ('_back', '_diag_line'):
            shape = diacanvas.shape.Path()
            shape.set_line_width(2.0)
            #shape.set_fill(False)
            #shape.set_fill_color(diacanvas.color(255, 255, 255))
            setattr(self, attr, shape)

    def update_compartment_common(self, affine, w, h):

        w, h = ClassifierItem.update_compartment_common(self, affine, w, h)

        d = self.DEPTH

        self._back.line(((0, 0), (d, -d), (w + d, -d), (w + d, h - d), (w, h)))
        self._diag_line.line(((w, 0), (w + d, -d)))

        return w, h

    def on_update(self, affine):
        ClassifierItem.on_update(self, affine)

        d = self.DEPTH
        x0, y0, x1, y1 = self.bounds
        self.set_bounds((x0, y0 - d, x1 + d, y1))

    def on_shape_iter(self):
        for s in ClassifierItem.on_shape_iter(self):
            yield s
        yield self._back
        yield self._diag_line

initialize_item(NodeItem, UML.Component)
