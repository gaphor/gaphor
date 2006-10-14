"""
Action diagram item.
"""

from math import pi

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphas.util import text_align, text_extents

class ActionItem(NamedItem):
    __uml__      = UML.Action
#    __s_valign__ = V_ALIGN_MIDDLE

    def draw(self, context):
        """
        Draw action symbol.
        """
        c = context.cairo

        d = 15

        c.move_to(0, d)
        c.arc(d, d, d, pi, 1.5 * pi)
        c.line_to(self.width - d, 0)
        c.arc(self.width - d, d, d, 1.5 * pi, 0)
        c.line_to(self.width, self.height - d)
        c.arc(self.width - d, self.height - d, d, 0, 0.5 * pi)
        c.line_to(d, self.height)
        c.arc(d, self.height - d, d, 0.5 * pi, pi)
        c.close_path()

        c.stroke()

        super(ActionItem, self).draw(context)



# vim:sw=4:et
