'''
eseCaseItempango diagram item
'''
# vim:sw=4

from __future__ import generators

import gobject
import pango
import diacanvas
from gaphor import UML
from gaphor.diagram import initialize_item
from nameditem import NamedItem

class UseCaseItem(NamedItem):
    MARGIN_X=60
    MARGIN_Y=30

    def __init__(self, id=None):
        NamedItem.__init__(self, id)
        self.set(height=50, width=100)
        self._border = diacanvas.shape.Ellipse()
        self._border.set_line_width(2.0)

    # DiaCanvasItem callbacks:

    def on_update(self, affine):
        # Center the text
        w, h = self.get_name_size()
        self.set(min_width=w + UseCaseItem.MARGIN_X,
                 min_height=h + UseCaseItem.MARGIN_Y)
        self.update_name(x=0, y=(self.height - h) / 2,
                         width=self.width, height=h)

        NamedItem.on_update(self, affine)

        self._border.ellipse(center=(self.width / 2, self.height / 2),
                              width=self.width, height=self.height)
        self.expand_bounds(1.0)

    def on_shape_iter(self):
        yield self._border
        for s in NamedItem.on_shape_iter(self):
            yield s


initialize_item(UseCaseItem, UML.UseCase)
