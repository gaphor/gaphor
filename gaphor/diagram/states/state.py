"""
State diagram item.
"""

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_TOP
from math import pi

DX = 15
DY = 8
DDX = 0.4 * DX
DDY = 0.4 * DY

class VertexItem(NamedItem):
    pass

class StateItem(VertexItem):
    __uml__   = UML.State
    __style__ = {
        'min-size':   (50, 30),
        'name-align': (ALIGN_CENTER, ALIGN_TOP),
    }


    def draw(self, context):
        """
        Draw state symbol.
        """
        super(StateItem, self).draw(context)

        c = context.cairo


        c.move_to(0, DY)
        c.curve_to(0, DDY, DDX, 0, DX, 0)
        c.line_to(self.width - DX, 0)
        c.curve_to(self.width - DDX, 0, self.width, DDY, self.width, DY)
        c.line_to(self.width, self.height - DY)
        c.curve_to(self.width, self.height - DDY,
                self.width - DDX, self.height,
                self.width - DX, self.height)
        c.line_to(DX, self.height)
        c.curve_to(DDX, self.height, 0, self.height - DDY, 0, self.height - DY)
        c.close_path()

        c.stroke()


# vim:sw=4:et
