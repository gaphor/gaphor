"""
Package diagram item.
"""

from gaphas.util import text_center, text_extents, text_set_font
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
        self.width = 100
        self.height = 50

    def pre_update(self, context):
        cr = context.cairo
        w, h = text_extents(cr, self.subject.name)
        self.min_width = w + 60
        self.min_height = h + 30 + self.TAB_Y
        if self.stereotype:
            s_w, s_h = text_extents(cr, self.stereotype)
            self.min_width = max(self.min_width, s_w)
            self.min_height += s_h

        super(PackageItem, self).pre_update(context)
        #self.n_align.margin = self.TAB_Y + 15, 30, 15, 30
        #self.s_align.margin = self.TAB_Y + 5, 30, 5, 30

        #self._border = diacanvas.shape.Path()
        #self._border.set_line_width(2.0)
        #self._shapes.add(self._border)

        #self.set(height = 50, width = 100)


    def draw(self, context):
        cr = context.cairo
        o = 0.0
        h = self.height
        w = self.width
        x = PackageItem.TAB_X
        y = PackageItem.TAB_Y
        cr.move_to(x, y)
        cr.line_to(x, o)
        cr.line_to(o, o)
        cr.line_to(o, h)
        cr.line_to(w, h)
        cr.line_to(w, y)
        cr.line_to(o, y)
        cr.stroke()
        if self.stereotype:
            text_center(cr, w / 2, y + 10, self.stereotype)

        text_set_font(cr, self.FONT_NAME)
        text_center(cr, w/2, y + (h-y)/2, self.subject.name)


# vim:sw=4:et
