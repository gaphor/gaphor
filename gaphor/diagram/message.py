"""
Sequence and communication diagram messages.

Messages are implemented according to UML 2.1.1 specification.

Implementation Details
======================
Message sort is supported but occurence specification is not implemented.
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
Occurence specification is not implemented, therefore
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

from gaphas.util import path_ellipse

from gaphor import UML
from gaphor.diagram.diagramline import NamedLine


class MessageItem(NamedLine):
    def _draw_circle(self, cr):
        """
        Draw circle for lost/found messages.
        """
        # method is called by draw_head or by draw_tail methods,
        # so draw in (0, 0))
        cr.set_line_width(0.01)
        cr.arc(0.0, 0.0, 4, 0.0, 2 * pi)
        cr.fill()


    def _draw_arrow(self, cr, half=False, filled=True):
        """
        Draw an arrow.

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
        cr.move_to(0, 0)

        subject = self.subject
        if subject and subject.messageKind == 'found':
            self._draw_circle(cr)
            cr.stroke()

        cr.move_to(0, 0)


    def draw_tail(self, context):
        cr = context.cairo
        subject = self.subject

        if subject and subject.messageSort in ('createMessage', 'reply'):
            cr.set_dash((7.0, 5.0), 0)

        cr.line_to(0, 0)
        cr.stroke()

        cr.set_dash((), 0)

        if subject:
            w = cr.get_line_width()
            if subject.messageKind == 'lost':
                self._draw_circle(cr)
                cr.stroke()

            cr.set_line_width(w)
            half = subject.messageSort == 'asynchSignal'
            filled = subject.messageSort in ('synchCall', 'deleteMessage')
            self._draw_arrow(cr, half, filled)
        else:
            self._draw_arrow(cr)

        cr.stroke()


    def draw(self, context):
        subject = self.subject
        super(MessageItem, self).draw(context)


# vim:sw=4:et
