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
    def draw_tail(self, context):
        cr = context.cairo
        cr.line_to(0, 0)
        cr.stroke()
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)


    def draw(self, context):
        super(MessageItem, self).draw(context)
        cr = context.cairo

        subject = self.subject
        if subject:
            if self.subject.messageKind == 'lost':
                pos = self.tail.pos
            elif self.subject.messageKind == 'found':
                pos = self.head.pos
            else:
                pos = None

            if pos:
                # draw circle for lost/found messages
                r = 10
                path_ellipse(cr, pos[0], pos[1], r, r)
                cr.set_line_width(0.01)
                cr.fill()


    def set_sort(self, ms):
        """
        Set message sort.
        """
        subject = self.subject
        if subject:
            subject.messageSort = ms


# vim:sw=4:et
