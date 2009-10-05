"""
Interaction diagram item.
"""

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_TOP

class InteractionItem(NamedItem):

    __uml__ = UML.Interaction

    __style__ = {
        'min-size': (150, 100),
        'name-align': (ALIGN_TOP, ALIGN_LEFT),
    }

    def draw(self, context):
        super(InteractionItem, self).draw(context)
        cr = context.cairo
        cr.rectangle(0, 0, self.width, self.height)
        
        # draw pentagon
        w, h = self._header_size
        h2 = h / 2.0
        cr.move_to(0, h)
        cr.line_to(w - 4, h)
        cr.line_to(w, h2)
        cr.line_to(w, 0)
        cr.stroke()


# vim:sw=4:et
