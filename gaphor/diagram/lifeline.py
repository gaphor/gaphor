"""
Lifeline diagram item.

Implementation Details
======================

Represented Classifier
----------------------
It is not clear how to attach a connectable element to a lifeline. For now,
``Lifeline.represents`` is ``None``. Ideas:
- drag and drop classifier from tree onto a lifeline
- match lifeline's name with classifier's name (what about namespace?)
- connect message to classifier, then classifier becomes a lifeline

Destruction Event
-----------------
Occurence specification is not implemented, therefore destruction event
cannot be supported. Still, destruction event notation is shown at the
bottom of the lifeline's lifetime when delete message is connected to a
lifeline.
"""

import gaphas
from gaphas.item import SW, SE
from gaphas.solver import STRONG
from gaphas.geometry import distance_line_point, Rectangle
from gaphas.constraint import LessThanConstraint, EqualsConstraint, CenterConstraint

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_MIDDLE

class LifetimeItem(object):
    """
    Attributes:

    - _is_destroyed: check if delete message is connected
    """

    MIN_LENGTH = 10

    def __init__(self):
        super(LifetimeItem, self).__init__()
        self._handles = [gaphas.Handle(strength=STRONG - 1), gaphas.Handle(strength=STRONG)]

        self._handles[0].movable = False
        self._handles[0].visible = False
        self._messages_count = 0
        self._is_destroyed = False

        # create constraint to keep bottom handle below top handle
        top, bottom = self._handles
        self._c_length = LessThanConstraint(smaller=top.y,
                bigger=bottom.y,
                delta=LifetimeItem.MIN_LENGTH)


    top = property(lambda s: s._handles[0])

    bottom = property(lambda s: s._handles[1])

    length = property(lambda s: s._handles[1].y - s._handles[0].y)

    def _set_destroyed(self, is_destroyed):
        self._is_destroyed = is_destroyed

    is_destroyed = property(lambda s: s._is_destroyed, _set_destroyed)


    def _is_visible(self):
        top, bottom = self._handles
        return bottom.y - top.y > self.MIN_LENGTH

    is_visible = property(_is_visible)


    def pre_update(self, context):
        # if lifetime is visible and there are messages connected, then
        # disallow hiding of lifetime
        if not self.is_visible and self._messages_count > 0:
            self._c_length.delta = LifetimeItem.MIN_LENGTH * 3 
        elif self._messages_count == 0:
            self._c_length.delta = LifetimeItem.MIN_LENGTH


    def draw(self, context):
        if context.hovered or context.focused or self.is_visible:
            cr = context.cairo
            cr.save()
            cr.set_dash((7.0, 5.0), 0)
            th, bh = self._handles
            cr.move_to(th.x, th.y)
            cr.line_to(bh.x, bh.y)
            cr.stroke()
            cr.restore()

            # draw destruction event
            if self._is_destroyed:
                d1 = 8
                d2 = d1 * 2
                cr.move_to(bh.x - d1, bh.y - d2)
                cr.line_to(bh.x + d1, bh.y)
                cr.move_to(bh.x - d1, bh.y)
                cr.line_to(bh.x + d1, bh.y - d2)
                cr.stroke()

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
            self._lifetime._c_length,
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
