"""
Lifeline diagram item.
"""

import gaphas
from gaphas.item import SW, SE
from gaphas.solver import STRONG
from gaphas.geometry import distance_line_point, Rectangle
from gaphas.constraint import EqualsConstraint, CenterConstraint

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_MIDDLE

class LifetimeItem(object):

    MIN_LENGTH = 10

    def __init__(self):
        super(LifetimeItem, self).__init__()
        self._handles = [gaphas.Handle(strength=STRONG), gaphas.Handle(strength=STRONG)]

        self._handles[0].movable = False
        self._handles[0].visible = False

    top_handle = property(lambda s: s._handles[0])

    bottom_handle = property(lambda s: s._handles[1])

    length = property(lambda s: s._handles[1].y - s._handles[0].y)

    def is_visible(self):
        top, bottom = self._handles
        return bottom.y - top.y > self.MIN_LENGTH

    def pre_update(self, context):
        top, bottom = self._handles
        if bottom.y - top.y < LifetimeItem.MIN_LENGTH:
            bottom.y = top.y + LifetimeItem.MIN_LENGTH

    def update(self, context):
        pass

    def draw(self, context):
        if context.hovered or context.focused or self.is_visible():
            cr = context.cairo
            cr.save()
            cr.set_dash((7.0, 5.0), 0)
            th, bh = self._handles
            cr.move_to(th.x, th.y)
            cr.line_to(bh.x, bh.y)
            cr.stroke()
            cr.restore()

    def handles(self):
        return self._handles


class LifelineItem(NamedItem):

    __uml__      = UML.Lifeline
    __style__ = {
        'name-align': (ALIGN_CENTER, ALIGN_MIDDLE),
    }

    def __init__(self, id = None):
        NamedItem.__init__(self, id)

        self._lifetime = LifetimeItem()
        top, bottom = self._lifetime.handles()
        self._handles.append(top)
        self._handles.append(bottom)

        constraints = [
            # Apply constraint to bottom, since bottom can be moved (top can't)
            CenterConstraint(self._handles[SW].x, self._handles[SE].x, bottom.x),
            EqualsConstraint(top.x, bottom.x),
            EqualsConstraint(self._handles[SW].y, top.y),
        ]
        self._constraints.extend(constraints)


    lifetime = property(lambda s: s._lifetime)


    def save(self, save_func):
        super(LifelineItem, self).save(save_func)
        top, bottom = self._lifetime.handles()
        save_func("lifetime-length", bottom.y - top.y)


    def load(self, name, value):
        if name == 'lifetime-length':
            top, bottom = self._lifetime.handles()
            bottom.y = self.height + float(value)
        else:
            super(LifelineItem, self).load(name, value)


    def pre_update(self, context):
        super(LifelineItem, self).pre_update(context)
        self._lifetime.pre_update(context)


    def update(self, context):
        super(LifelineItem, self).update(context)
        #self._lifetime.update(context)


    def draw(self, context):
        super(LifelineItem, self).draw(context)
        cr = context.cairo
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()
        self._lifetime.draw(context)


    def point(self, x, y):
        d1 = super(LifelineItem, self).point(x, y)
        h1, h2 = self._lifetime.handles()
        d2 = distance_line_point(h1.pos, h2.pos, (x, y))[0]
        return min(d1, d2)


# vim:sw=4:et
