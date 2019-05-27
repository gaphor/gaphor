"""
Package diagram item.
"""

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem


class PackageItem(NamedItem):

    __uml__ = UML.Package, UML.Profile
    __stereotype__ = {"profile": UML.Profile}
    __style__ = {
        "min-size": (NamedItem.style.min_size[0], 70),
        "name-font": "sans bold 10",
        "name-padding": (25, 10, 5, 10),
        "tab-x": 50,
        "tab-y": 20,
    }

    def __init__(self, id=None, model=None):
        super(PackageItem, self).__init__(id, model)

    def draw(self, context):
        super(PackageItem, self).draw(context)

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


# vim:sw=4:et
