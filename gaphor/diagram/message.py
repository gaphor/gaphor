'''
Relationship -- Base class for dependencies and associations.
'''
# vim:sw=4:et

import gobject
import diacanvas

from gaphor import resource, UML
from gaphor.diagram import initialize_item

from gaphor.diagram.diagramline import DiagramLine

class MessageItem(DiagramLine):
    
    def __init__(self, id=None):
        DiagramLine.__init__(self, id)
        self.set(has_tail=1, tail_fill_color=0, tail_a=0.0, tail_b=15.0, tail_c=6.0, tail_d=6.0)

    def save (self, save_func):
        DiagramLine.save(self, save_func)

    def load (self, name, value):
        DiagramLine.load(self, name, value)

    def postload(self):
        DiagramLine.postload(self)

    def allow_connect_handle(self, handle, connecting_to):
        """See RelationshipItem.allow_connect_handle().
        """
        try:
            return isinstance(connecting_to.subject, UML.Lifeline)
        except AttributeError:
            return 0

    def confirm_connect_handle(self, handle):
        """See RelationshipItem.confirm_connect_handle().

        Always create a new Message with two EventOccurence instances.
        """
        #print 'confirm_connect_handle', handle, self.subject
        c1 = self.handles[0].connected_to
        c2 = self.handles[-1].connected_to
        if c1 and c2:
            s1 = c1.subject
            s2 = c2.subject
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

initialize_item(MessageItem)
