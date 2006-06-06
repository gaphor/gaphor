"""
Package diagram item.
"""

import gobject
import pango
import diacanvas
from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.align import MARGIN_TOP

class PackageItem(NamedItem):

    __uml__ = UML.Package, UML.Profile
    __stereotype__ = {
        'profile': UML.Profile,
    }

    TAB_X = 50
    TAB_Y = 20

    def __init__(self, id=None):
        NamedItem.__init__(self, id)

        self.n_align.margin = self.TAB_Y + 15, 30, 15, 30
        self.s_align.margin = self.TAB_Y + 5, 30, 5, 30

        self._border = diacanvas.shape.Path()
        self._border.set_line_width(2.0)
        self._shapes.add(self._border)

        self.set(height = 50, width = 100)


    def on_update(self, affine):
        NamedItem.on_update(self, affine)

        o = 0.0
        h = self.height
        w = self.width
        x = PackageItem.TAB_X
        y = PackageItem.TAB_Y
        line = ((x, y), (x, o), (o, o), (o, h), (w, h), (w, y), (o, y))
        self._border.line(line)
        self.expand_bounds(1.0)

# vim:sw=4:et
