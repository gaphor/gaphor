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

from gaphas.item import SW, SE
from gaphas.connector import Handle, LinePort
from gaphas.solver import STRONG
from gaphas.geometry import distance_line_point, Rectangle
from gaphas.constraint import (
    LessThanConstraint,
    EqualsConstraint,
    CenterConstraint,
    LineAlignConstraint,
)

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_MIDDLE


class LifetimePort(LinePort):
    def constraint(self, canvas, item, handle, glue_item):
        """
        Create connection line constraint between item's handle and the
        port.
        """
        line = canvas.project(glue_item, self.start, self.end)
        point = canvas.project(item, handle.pos)

        x, y = canvas.get_matrix_i2c(item).transform_point(*handle.pos)
        x, y = canvas.get_matrix_c2i(glue_item).transform_point(x, y)

        # keep message at the same distance from head or bottom of lifetime
        # line depending on situation
        height = self.end.y - self.start.y
        if y / height < 0.5:
            delta = y - self.start.y
            align = 0
        else:
            delta = y - self.end.y
            align = 1
        return LineAlignConstraint(line, point, align, delta)


class LifetimeItem:
    """
    Lifeline's lifetime object.

    Provides basic properties of lifeline's lifetime.

    :Attributes:
     top
        Top handle.
     bottom
        Bottom handle.
     port
        Lifetime connection port.
     visible
        Determines port visibility.
     min_length
        Minimum length of lifetime.
     length
        Length of lifetime.
    """

    MIN_LENGTH = 10
    MIN_LENGTH_VISIBLE = 3 * MIN_LENGTH

    def __init__(self):
        super(LifetimeItem, self).__init__()

        self.top = Handle(strength=STRONG - 1)
        self.bottom = Handle(strength=STRONG)

        self.top.movable = False
        self.top.visible = False

        self.port = LifetimePort(self.top.pos, self.bottom.pos)
        self.visible = False

        self._c_min_length = None  # to be set by lifeline item

    def _set_length(self, length):
        """
        Set lifeline's lifetime length.
        """
        self.bottom.pos.y = self.top.pos.y + length

    length = property(lambda s: s.bottom.pos.y - s.top.pos.y, _set_length)

    def _set_min_length(self, length):
        assert self._c_min_length is not None
        self._c_min_length.delta = length

    min_length = property(lambda s: s._c_min_length.delta, _set_min_length)

    def _set_connectable(self, connectable):
        self.port.connectable = connectable
        self.bottom.movable = connectable

    connectable = property(lambda s: s.port.connectable, _set_connectable)

    def _is_visible(self):
        return self.length > self.MIN_LENGTH

    def _set_visible(self, visible):
        """
        Set lifetime visibility.
        """
        if visible:
            self.bottom.pos.y = self.top.pos.y + 3 * self.MIN_LENGTH
        else:
            self.bottom.pos.y = self.top.pos.y + self.MIN_LENGTH

    visible = property(_is_visible, _set_visible)


class LifelineItem(NamedItem):
    """
    Lifeline item.

    The item represents head of lifeline. Lifeline's lifetime is
    represented by `lifetime` instance.

    :Attributes:
     lifetime
        Lifeline's lifetime part.
     is_destroyed
        Check if delete message is connected.
    """

    __uml__ = UML.Lifeline
    __style__ = {"name-align": (ALIGN_CENTER, ALIGN_MIDDLE)}

    def __init__(self, id=None, model=None):
        NamedItem.__init__(self, id, model)

        self.is_destroyed = False

        self.lifetime = LifetimeItem()

        top = self.lifetime.top
        bottom = self.lifetime.bottom

        self._handles.append(top)
        self._handles.append(bottom)
        self._ports.append(self.lifetime.port)

    def setup_canvas(self):
        super(LifelineItem, self).setup_canvas()

        top = self.lifetime.top
        bottom = self.lifetime.bottom

        # create constraints to:
        # - keep bottom handle below top handle
        # - keep top and bottom handle in the middle of the head
        c1 = CenterConstraint(
            self._handles[SW].pos.x, self._handles[SE].pos.x, bottom.pos.x
        )

        c2 = EqualsConstraint(top.pos.x, bottom.pos.x, delta=0.0)

        c3 = EqualsConstraint(self._handles[SW].pos.y, top.pos.y, delta=0.0)
        self.lifetime._c_min_length = LessThanConstraint(
            top.pos.y, bottom.pos.y, delta=LifetimeItem.MIN_LENGTH
        )
        self.__constraints = (c1, c2, c3, self.lifetime._c_min_length)

        list(map(self.canvas.solver.add_constraint, self.__constraints))

    def teardown_canvas(self):
        super(LifelineItem, self).teardown_canvas()
        list(map(self.canvas.solver.remove_constraint, self.__constraints))

    def save(self, save_func):
        super(LifelineItem, self).save(save_func)
        save_func("lifetime-length", self.lifetime.length)

    def load(self, name, value):
        if name == "lifetime-length":
            self.lifetime.bottom.pos.y = self.height + float(value)
        else:
            super(LifelineItem, self).load(name, value)

    def draw(self, context):
        """
        Draw lifeline.

        Lifeline's head is always drawn.

        Lifeline's lifetime is drawn when lifetime is visible.
        """
        super(LifelineItem, self).draw(context)
        cr = context.cairo
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

        if context.hovered or context.focused or self.lifetime.visible:
            top = self.lifetime.top
            bottom = self.lifetime.bottom
            cr = context.cairo
            cr.save()
            cr.set_dash((7.0, 5.0), 0)
            cr.move_to(top.pos.x, top.pos.y)
            cr.line_to(bottom.pos.x, bottom.pos.y)
            cr.stroke()
            cr.restore()

            # draw destruction event
            if self.is_destroyed:
                d1 = 8
                d2 = d1 * 2
                cr.move_to(bottom.pos.x - d1, bottom.pos.y - d2)
                cr.line_to(bottom.pos.x + d1, bottom.pos.y)
                cr.move_to(bottom.pos.x - d1, bottom.pos.y)
                cr.line_to(bottom.pos.x + d1, bottom.pos.y - d2)
                cr.stroke()

    def point(self, pos):
        """
        Find distance to lifeline item.

        Distance to lifeline's head and lifeline's lifetime is calculated
        and minimum is returned.
        """
        d1 = super(LifelineItem, self).point(pos)
        top = self.lifetime.top
        bottom = self.lifetime.bottom
        d2 = distance_line_point(top.pos, bottom.pos, pos)[0]
        return min(d1, d2)


# vim:sw=4:et
