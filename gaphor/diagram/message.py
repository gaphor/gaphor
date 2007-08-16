"""
Message - sequence diagram messages.
"""

from gaphas.util import path_ellipse

from gaphor import UML
from gaphor.diagram.diagramline import NamedLine


#
# TODO: asynch message has open arrow head
# synch message: closed arrow head, open arrow head and a dashed line.
# object creation: open arrow head, dashed line.

#Syntax for the Message name is the following:
#  messageident ::= [attribute =] signal-or-operation-name [ ( arguments) ][: return-value] | *
#  arguments ::= argument [ , arguments]
#  argument ::= [parameter-name=]argument-value | attribute= out-parameter-name [:argument-value]| -
#
# Message.signature points to the operation or signal that is executed
# Message.arguments provides a list of arguments for the operation.
#
class MessageItem(NamedLine):
    def _draw_circle(self, cr):
        """
        Draw circle for lost/found messages.
        """
        cr.save()
        r = 10
        # method is called by draw_head or by draw_tail methods,
        # so draw in (0, 0))
        path_ellipse(cr, 0, 0, r, r)
        cr.fill_preserve()
        cr.restore()


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


    def set_sort(self, ms):
        """
        Set message sort.
        """
        subject = self.subject
        if subject:
            subject.messageSort = ms
            self.request_update()


# vim:sw=4:et
