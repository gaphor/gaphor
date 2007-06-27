"""
Lifeline diagram item.
"""

import gaphas
from gaphas.solver import Variable
from gaphas.constraint import EqualsConstraint

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_MIDDLE

class LifetimeItem(gaphas.Item):
    def __init__(self):
        super(LifetimeItem, self).__init__()
        self._handle = gaphas.Handle()
        self._handles.append(self._handle)
        self._y0 = 0


    def set_pos(self, x, y):
        self._handle.x = x
        self._y0 = y


    def update(self, context):
        super(LifetimeItem, self).update(context)
        h = self._handle
        dy = max(10, h.y - self._y0)
        h.y = self._y0 + dy


    def draw(self, context):
        cr = context.cairo
        cr.set_line_width(10)
        h = self._handle
        cr.move_to(h.x, self._y0)
        cr.line_to(h.x, h.y)


# Lifeline semantics:
#  lifeline_name[: class_name]
#  lifeline_name: str
#  class_name: name of referenced ConnectableElement
class LifelineItem(NamedItem):
    __uml__      = UML.Lifeline
    __style__ = {
        'name-align': (ALIGN_CENTER, ALIGN_MIDDLE),
    }

    def __init__(self, id = None):
        NamedItem.__init__(self, id)

        self._has_lifetime = False
        lt = self._lifetime = LifetimeItem()
        self._items.append(lt)

        x, y = self.style.min_size
        lt.set_pos(x / 2.0, y)


    def update(self, context):
        super(LifelineItem, self).update(context)
        self._lifetime.set_pos(self.width / 2.0, self.height)


    def draw(self, context):
        super(LifelineItem, self).draw(context)

        cr = context.cairo
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()


# vim:sw=4:et
