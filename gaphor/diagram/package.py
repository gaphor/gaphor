"""
Package diagram item.
"""

from gaphas.util import text_center, text_extents, text_set_font
from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
import font

class PackageItem(NamedItem):

    __uml__ = UML.Package, UML.Profile
    __stereotype__ = {
        'profile': UML.Profile,
    }
    __style__ = {
        'name-padding': (25, 10, 5, 10),
    }

    TAB_X = 50
    TAB_Y = 20

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

        super(PackageItem, self).draw(context)


# vim:sw=4:et
