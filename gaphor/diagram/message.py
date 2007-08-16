"""
Sequence and communication diagram messages.

Messages are implemented according to UML 2.1.1 specification.

Implementation Issues
=====================
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

Asynchronous Message
--------------------
It is not clear how to draw asynchronous messages. 

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
"""

from gaphas.util import path_ellipse

from gaphor import UML
from gaphor.diagram.diagramline import NamedLine


class MessageItem(NamedLine):
    def _draw_circle(self, cr):
        """
        Draw circle for lost/found messages.
        """
        r = 8
        # method is called by draw_head or by draw_tail methods,
        # so draw in (0, 0))
        path_ellipse(cr, 0, 0, r, r)
        cr.fill_preserve()


    def draw_head(self, context):
        super(MessageItem, self).draw_head(context)
        cr = context.cairo

        subject = self.subject
        if subject and subject.messageKind == 'found':
            self._draw_circle(cr)


    def draw_tail(self, context):
        super(MessageItem, self).draw_tail(context)

        cr = context.cairo

        subject = self.subject
        if subject and subject.messageKind == 'lost':
            self._draw_circle(cr)

        # we need always some kind of arrow...
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)

        # ... which should be filled arrow in some cases
        # no subject - draw like synchronous call
        if not subject or subject.messageSort == 'synchCall':
            cr.close_path()
            cr.fill_preserve()

        cr.stroke()


    def draw(self, context):
        subject = self.subject
        if subject and subject.messageSort in ('createMessage', 'reply'):
            cr = context.cairo
            cr.set_dash((7.0, 5.0), 0)

        super(MessageItem, self).draw(context)


# vim:sw=4:et
