"""
Package diagram item.
"""

from gaphas.util import text_align, text_extents, text_set_font
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
        'tab-x': 50,
        'tab-y': 20,
    }

    def pre_update(self, context):
        cr = context.cairo
        w, h = text_extents(cr, self.subject.name)
        self.min_width = w + 60
        self.min_height = h + 30 + self.style.tab_y
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
        x = self.style.tab_x
        y = self.style.tab_y
        cr.move_to(x, y)
        cr.line_to(x, o)
        cr.line_to(o, o)
        cr.line_to(o, h)
        cr.line_to(w, h)
        cr.line_to(w, y)
        cr.line_to(o, y)
        cr.stroke()
        if self.stereotype:
            y += 10
            text_align(cr, w / 2, y, self.stereotype)
            y += 10

        if self.subject and self.subject.name:
            text_align(cr, w / 2, y + 10, self.subject.name)


# vim:sw=4:et
