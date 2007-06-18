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
        super(PackageItem, self).draw(context)


# vim:sw=4:et
