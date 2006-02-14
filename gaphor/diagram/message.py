'''
Relationship -- Base class for dependencies and associations.
'''
# vim:sw=4:et

import gobject
import pango
import diacanvas

from gaphor import resource, UML

from gaphor.diagram.diagramline import DiagramLine
from gaphor.diagram.lifeline import LifelineItem, LifetimeItem
from gaphor.diagram import TextElement
from gaphor.diagram.groupable import GroupBase

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

        DiagramLine.on_update(self, affine)
        GroupBase.on_update(self, affine)


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
        c1 = self.handles[0].connected_to
        c2 = self.handles[-1].connected_to
        if c1 and c2:
            assert c1.__class__ == c2.__class__
            s1 = c1.subject
            s2 = c2.subject
            if self.subject and \
               self.subject.sendEvent.covered is s1 and \
               self.subject.receiveEvent.covered is s2:
                return

            factory = resource(UML.ElementFactory)
            message = factory.create(UML.Message)
            message.messageKind = 'complete'
            head_event = factory.create(UML.EventOccurrence)
            head_event.sendMessage = message
            head_event.covered = s1

            tail_event = factory.create(UML.EventOccurrence)
            tail_event.receiveMessage = message
            tail_event.covered = s2

            self.set_subject(message)

    def confirm_disconnect_handle(self, handle, was_connected_to):
        """See RelationshipItem.confirm_disconnect_handle().
        """
        self.set_subject(None)
