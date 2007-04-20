"""
Message - sequence diagram messages.
"""

import itertools

from gaphor import UML

from gaphor.diagram.diagramline import DiagramLine
from gaphor.diagram.lifeline import LifelineItem, LifetimeItem
#from gaphor.diagram import TextElement

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
class MessageItem(DiagramLine, GroupBase):
    
    FONT='sans 10'

    def __init__(self, id=None):
        GroupBase.__init__(self)
        DiagramLine.__init__(self, id)

        self._name  = TextElement('name')
        self.add(self._name)

        self._circle = diacanvas.shape.Ellipse()
        #self._circle.set_line_width(2.0)
        self._circle.set_fill_color(diacanvas.color(0, 0, 0))
        self._circle.set_fill(diacanvas.shape.FILL_SOLID)

        self.set(has_tail = 1, tail_fill_color = 0, tail_a = 0.0,
            tail_b = 15.0, tail_c = 6.0, tail_d = 6.0)


    def on_subject_notify(self, pspec, notifiers=()):
        DiagramLine.on_subject_notify(self, pspec, notifiers)
        if self.subject:
            self._name.subject = self.subject
        self.request_update()


    def on_update(self, affine):
        handles = self.handles
        middle = len(handles)/2

        def get_pos_centered(p1, p2, width, height):
            x = p1[0] > p2[0] and width + 2 or -2
            x = (p1[0] + p2[0]) / 2.0 - x
            y = p1[1] <= p2[1] and height or 0
            y = (p1[1] + p2[1]) / 2.0 - y
            return x, y

        p1 = handles[middle-1].get_pos_i()
        p2 = handles[middle].get_pos_i()

        w, h = self._name.get_size()
        x, y = get_pos_centered(p1, p2, w, h)
        self._name.update_label(x, y)

        if self.subject:
            if self.subject.messageKind == 'lost':
                x, y = self.handles[-1].get_pos_i()
            if self.subject.messageKind == 'found':
                x, y = self.handles[0].get_pos_i()
            self._circle.ellipse((x, y), 10, 10)

        DiagramLine.on_update(self, affine)
        GroupBase.on_update(self, affine)
        

    def on_shape_iter(self):
        """
        Return activity edge name and circle.
        """
        it = DiagramLine.on_shape_iter(self)
        if self.subject and self.subject.messageKind in ('lost', 'found'):
            return itertools.chain(it, [self._circle])
        else:
            return it


    #
    # Gaphor Connection Protocol
    #
    def allow_connect_handle(self, handle, item):
        """
        """
        if isinstance(item, (LifelineItem, LifetimeItem)):
            if handle is self.handles[0]:
                c = self.handles[-1].connected_to
            else:
                c = self.handles[0].connected_to
            return c is None or isinstance(item, c.__class__)
        else:
            return False


    def confirm_connect_handle(self, handle):
        """See RelationshipItem.confirm_connect_handle().

        Always create a new Message with two EventOccurence instances.
        """
        #print 'confirm_connect_handle', handle, self.subject
        send = self.handles[0].connected_to
        received = self.handles[-1].connected_to
        factory = resource(UML.ElementFactory)

        def get_subject(c):
            if not self.subject:
                factory = resource(UML.ElementFactory)
                message = factory.create(UML.Message)
                self.set_subject(message)
            return self.subject

        if send:
            message = get_subject(send)
            if not message.sendEvent:
                event = factory.create(UML.EventOccurrence)
                event.sendMessage = message
                event.covered = send.subject

        if received:
            message = get_subject(received)
            if not message.receiveEvent:
                event = factory.create(UML.EventOccurrence)
                event.receiveMessage = message
                event.covered = received.subject

        if send and received:
            assert send.__class__ == received.__class__
            kind = 'complete'
        elif send and not received:
            kind = 'lost'
        elif not send and received:
            kind = 'found'

        message.messageKind = kind


    def confirm_disconnect_handle(self, handle, was_connected_to):
        """See RelationshipItem.confirm_disconnect_handle().
        """
        send = self.handles[0].connected_to
        received = self.handles[-1].connected_to

        if send:
            self.subject.messageKind = 'lost'
            event = self.subject.receiveEvent
            if event:
                event.receiveMessage = None
                event.covered = None
                del event

        if received:
            self.subject.messageKind = 'found'
            event = self.subject.sendEvent
            if event:
                event.sendMessage = None
                event.covered = None
                del event

        if not send and not received:
            self.set_subject(None)

# vim:sw=4:et
