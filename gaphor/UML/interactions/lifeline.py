"""Lifeline diagram item.

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
Occurrence specification is not implemented, therefore destruction event
cannot be supported. Still, destruction event notation is shown at the
bottom of the lifeline's lifetime when delete message is connected to a
lifeline.
"""

from gaphas.connector import Handle, Port
from gaphas.constraint import CenterConstraint, EqualsConstraint, LessThanConstraint
from gaphas.geometry import distance_line_point
from gaphas.item import SE, SW
from gaphas.position import MatrixProjection, Position
from gaphas.solver import VERY_STRONG, MultiConstraint
from gaphas.solver.constraint import BaseConstraint
from gaphas.types import Pos, SupportsFloatPos

from gaphor import UML
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, Text, cairo_state, stroke
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontWeight
from gaphor.UML.recipes import stereotypes_str


class BetweenConstraint(BaseConstraint):
    """b <= a <= c.

    Only a will change.
    """

    def __init__(self, v, lower, upper):
        super().__init__(v, lower, upper)
        self.v = v
        self.lower = lower
        self.upper = upper

    def solve_for(self, var):
        if var is not self.v:
            return

        lower = self.lower.value
        upper = self.upper.value
        if lower > upper:
            lower, upper = upper, lower
        if self.v.value < lower:
            self.v.value = lower
        if self.v.value > upper:
            self.v.value = upper


class BetweenPort(Port):
    """Port defined as a line between two handles."""

    def __init__(self, start: Position, end: Position) -> None:
        super().__init__()

        self.start = start
        self.end = end

    def glue(self, pos: SupportsFloatPos) -> tuple[Pos, float]:
        d, pl = distance_line_point(
            self.start.tuple(), self.end.tuple(), (float(pos[0]), float(pos[1]))
        )
        return pl, d

    def constraint(self, item, handle, glue_item):
        """Create connection line constraint between item's handle and the
        port."""
        start = MatrixProjection(self.start, glue_item.matrix_i2c)
        end = MatrixProjection(self.end, glue_item.matrix_i2c)
        point = MatrixProjection(handle.pos, item.matrix_i2c)

        cx = EqualsConstraint(point.x, start.x)
        cy = BetweenConstraint(point.y, start.y, end.y)

        return MultiConstraint(start, end, point, cx, cy)


class LifetimeItem:
    """Lifeline's lifetime object.

    Provides basic properties of lifeline's lifetime.

    Attributes:
        top: Top handle.
        bottom: Bottom handle.
        port: Lifetime connection port.
        visible: Determines port visibility.
    """

    MIN_LENGTH = 10
    MIN_LENGTH_VISIBLE = 3 * MIN_LENGTH

    def __init__(self):
        super().__init__()

        self.top = Handle(strength=VERY_STRONG - 1)
        self.bottom = Handle(strength=VERY_STRONG)

        self.top.movable = False
        self.top.visible = False

        self.port = BetweenPort(self.top.pos, self.bottom.pos)

        self._c_min_length = None  # to be set by lifeline item

    def _set_length(self, length):
        """Set lifeline's lifetime length."""
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
        """Set lifetime visibility."""
        if visible:
            self.bottom.pos.y = self.top.pos.y + self.MIN_LENGTH_VISIBLE
        else:
            self.bottom.pos.y = self.top.pos.y + self.MIN_LENGTH

    visible = property(_is_visible, _set_visible)


@represents(UML.Lifeline)
class LifelineItem(ElementPresentation[UML.Lifeline], Named):
    """Lifeline item.

    The item represents the head of the lifeline. We represent the lifeline's
    lifetime by `lifetime` instance.

    Attributes:
        lifetime: Lifeline's lifetime part.
        is_destroyed: Check if delete message is connected.
    """

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self._connections = diagram.connections
        self.is_destroyed = False

        self.lifetime = LifetimeItem()

        top = self.lifetime.top
        bottom = self.lifetime.bottom

        self._handles.append(top)
        self._handles.append(bottom)
        self.watch_handle(top)
        self.watch_handle(bottom)
        self._ports.append(self.lifetime.port)

        self.shape = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(
                text=lambda: self.subject.name or "",
                style={"font-weight": FontWeight.BOLD},
            ),
            draw=self.draw_lifeline,
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.setup_constraints()

    def setup_constraints(self):
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

        for c in [c1, c2, c3, self.lifetime._c_min_length]:
            self._connections.add_constraint(self, c)

    def save(self, save_func):
        super().save(save_func)
        save_func("lifetime-length", self.lifetime.length)

    def load(self, name, value):
        if name == "lifetime-length":
            self.lifetime.bottom.pos.y = self.height + float(value)
        else:
            super().load(name, value)

    def draw_lifeline(self, box, context, bounding_box):
        """Draw lifeline.

        We always draw the lifeline's head. We only draw the lifeline's
        lifetime when the lifetime is visible.
        """
        cr = context.cairo
        cr.rectangle(0, 0, self.width, self.height)
        stroke(context)

        if (
            context.hovered
            or context.focused
            or context.dropzone
            or self.lifetime.visible
        ):
            bottom = self.lifetime.bottom
            cr = context.cairo
            with cairo_state(cr):
                cr.set_dash((7.0, 5.0), 0)
                top = self.lifetime.top
                cr.move_to(top.pos.x, top.pos.y)
                cr.line_to(bottom.pos.x, bottom.pos.y)
                stroke(context, dash=False)

            # draw destruction event
            if self.is_destroyed:
                d1 = 8
                d2 = d1 * 2
                cr.move_to(bottom.pos.x - d1, bottom.pos.y - d2)
                cr.line_to(bottom.pos.x + d1, bottom.pos.y)
                cr.move_to(bottom.pos.x - d1, bottom.pos.y)
                cr.line_to(bottom.pos.x + d1, bottom.pos.y - d2)
                cr.stroke()

    def point(self, x, y):
        """Find distance to lifeline item.

        We calculate the distance to the lifeline's head, and then we
        calculate the lifetime. We return the minimum.
        """
        d1 = super().point(x, y)
        top = self.lifetime.top
        bottom = self.lifetime.bottom
        d2 = distance_line_point(top.pos, bottom.pos, (x, y))[0]
        return min(d1, d2)
