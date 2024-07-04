"""Sequence and communication diagram messages.

Messages are implemented according to UML 2.1.1 specification.

Implementation Details
======================
Message sort is supported but occurrence specification is not implemented.
This means that model drawn on a diagram is not complete on UML datamodel
level, still it is valid UML diagram (see Lifelines Diagram in UML
specification, page 461).

Reply Messages
--------------
Different sources show that reply message has filled arrow, including
UML 2.0.

UML 2.1.1 specification says that reply message should be drawn with an
open arrow. This is visible on examples in UML 2.0 and UML 2.1.1
specifications.

Asynchronous Signal
--------------------
It is not clear how to draw signals. It is usually drawn with a half-open
arrow.  This approach is used in Gaphor, too.

Delete Message
--------------
Different sources show that delete message has a "X" at the tail.
It does not seem to be correct solution. A "X" should be shown
at the end of lifeline's lifetime instead (see ``lifeline`` module
documentation for more information).

Events
------
Occurrence specification is not implemented, therefore
- no events implemented (i.e. destroy event)
- no message sequence number on communication diagram

Operations
----------
``Lifeline.represents`` attribute is ``None``, so it is not possible to
specify operation (or signal) for a message. Instead, one has to put
operation information in message's name.

See also ``lifeline`` module documentation.
"""

from math import pi

from gaphas.connector import Handle
from gaphas.constraint import constraint

from gaphor import UML
from gaphor.diagram.presentation import (
    LinePresentation,
    Named,
    get_center_pos,
    text_name,
)
from gaphor.diagram.shapes import Box, cairo_state, stroke
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes
from gaphor.UML.interactions.lifeline import LifelineItem

PI_2 = pi / 2


@represents(UML.Message)
class MessageItem(Named, LinePresentation[UML.Message]):
    """Message item is drawn on sequence and communication diagrams.

    On communication diagram, message item is decorated with an arrow in
    the middle of a line.

    Multiple messages can be depicted via this one message item.

    Attributes:

    - _is_communication: check if message is on communication diagram
    - _arrow_pos: decorating arrow position
    - _arrow_angle: decorating arrow angle
    """

    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape_middle=Box(
                text_stereotypes(self),
                text_name(self),
            ),
        )
        self.handles()[1].pos = (40, 0)

        self._horizontal_line = constraint(horizontal=[h.pos for h in self.handles()])

        self._is_communication = False
        self._arrow_pos = 0, 0
        self._arrow_angle = 0

        self.watch("subject.name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject[Message].messageEnd", self._update_message_end)

    def load(self, name, value):
        if name == "points":
            self.diagram.connections.remove_constraint(self, self._horizontal_line)
        return super().load(name, value)

    def postload(self):
        super().postload()
        if len(self.handles()) == 2 and not self.is_communication():
            self.diagram.connections.add_constraint(self, self._horizontal_line)

    def insert_handle(self, index: int, handle: Handle) -> None:
        if len(self.handles()) == 2:
            self.diagram.connections.remove_constraint(self, self._horizontal_line)
        super().insert_handle(index, handle)

    def remove_handle(self, handle: Handle) -> None:
        super().remove_handle(handle)
        if len(self.handles()) == 2 and not self.is_communication():
            self.diagram.connections.add_constraint(self, self._horizontal_line)

    def _update_message_end(self, event):
        if self.is_communication():
            self.diagram.connections.remove_constraint(self, self._horizontal_line)
        elif len(self.handles()) == 2:
            self.diagram.connections.add_constraint(self, self._horizontal_line)

    def _draw_circle(self, cr):
        """Draw circle for lost/found messages."""
        # method is called by draw_head or by draw_tail methods,
        # so draw in (0, 0))
        cr.set_line_width(0.01)
        cr.arc(0.0, 0.0, 4, 0.0, 2 * pi)
        cr.fill()

    def _draw_arrow(self, cr, half=False, filled=True):
        """Draw an arrow.

        Parameters:

        - half: draw half-open arrow
        - filled: draw filled arrow
        """
        cr.move_to(15, 6)
        cr.line_to(0, 0)
        if not half:
            cr.line_to(15, -6)
        if filled:
            cr.close_path()
            cr.fill_preserve()

    def draw_head(self, context):
        cr = context.cairo
        # no head drawing in case of communication diagram
        if self._is_communication:
            cr.move_to(0, 0)
            return

        cr.move_to(0, 0)

        subject = self.subject
        if subject and subject.messageKind == "found":
            self._draw_circle(cr)
            cr.stroke()

        cr.move_to(0, 0)

    def draw_tail(self, context):
        cr = context.cairo

        # no tail drawing in case of communication diagram
        if self._is_communication:
            cr.line_to(0, 0)
            return

        subject = self.subject

        if subject and subject.messageSort in ("createMessage", "reply"):
            cr.set_dash((7.0, 5.0), 0)

        cr.line_to(0, 0)
        stroke(context, fill=False, dash=False)

        cr.set_dash((), 0)

        if subject:
            w = cr.get_line_width()
            if subject.messageKind == "lost":
                self._draw_circle(cr)
                cr.stroke()

            cr.set_line_width(w)
            half = subject.messageSort == "asynchSignal"
            filled = subject.messageSort in ("synchCall", "deleteMessage")
            self._draw_arrow(cr, half, filled)
        else:
            self._draw_arrow(cr)

        stroke(context, fill=False)

    def _draw_decorating_arrow(self, cr, inverted=False):
        with cairo_state(cr):
            angle: float = self._arrow_angle

            hint = 1 if abs(angle) >= PI_2 and angle != -PI_2 else -1
            if inverted:
                angle += hint * pi

            x, y = self._arrow_pos

            # move to arrow pos and rotate, below we operate in horizontal
            # mode
            cr.translate(x, y)
            cr.rotate(angle)
            # add some padding
            cr.translate(0, 6 * hint)

            # draw decorating arrow
            d = 15
            dr = d - 4
            r = 3
            cr.set_line_width(1.5)
            cr.move_to(-d, 0)
            cr.line_to(d, 0)
            cr.line_to(dr, r)
            cr.move_to(dr, -r)
            cr.line_to(d, 0)
            cr.stroke()

    def draw(self, context):
        self._is_communication = self.is_communication()
        super().draw(context)

        # on communication diagram draw decorating arrows for messages and
        # inverted messages
        if self._is_communication:
            pos, angle = get_center_pos(self.handles())
            self._arrow_pos = pos
            self._arrow_angle = angle
            cr = context.cairo
            self._draw_decorating_arrow(cr)

    def is_communication(self):
        """Check if message is connecting to lifelines on communication
        diagram."""
        c1 = self._connections.get_connection(self.head)
        c2 = self._connections.get_connection(self.tail)
        return (
            c1
            and isinstance(c1.connected, LifelineItem)
            and not c1.connected.lifetime.visible
            and (
                not c2
                or (
                    isinstance(c2.connected, LifelineItem)
                    and not c2.connected.lifetime.visible
                )
            )
        )
