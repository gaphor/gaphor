'''
Implementation - - - -|>
'''
# vim:sw=4

import gobject
import diacanvas
import gaphor
import gaphor.UML as UML
from gaphor.diagram import initialize_item
import relationship

class ImplementationItem(relationship.RelationshipItem):

    def __init__(self, id = None):
        relationship.RelationshipItem.__init__(self, id)
        self.set(dash = (7.0, 5.0), has_head = 1, head_fill_color = 0,
                 head_a = 15.0, head_b = 15.0, head_c = 10.0, head_d = 10.0)
        
    # Gaphor Connection Protocol

    def find_relationship(self, head_subject, tail_subject):
        """See RelationshipItem.find_relationship().
        """
        return self._find_relationship(head_subject, tail_subject,
           ('contract', None),
           ('implementatingClassifier', 'implementation'))


    def allow_connect_handle(self, handle, connecting_to):
        """
        Implementation can connect head to Interface and
        tail to BehavioredClassifier.
        """
        can_connect = False

        head = self.handles[0] 
        tail = self.handles[-1]

        if head is handle and isinstance(connecting_to.subject, UML.Interface):
            can_connect = True
        elif tail is handle and isinstance(connecting_to.subject, UML.BehavioredClassifier):
            can_connect = True

        assert not head.connected_to \
            or head.connected_to and isinstance(head.connected_to.subject, UML.Interface)
        assert not tail.connected_to or \
            tail.connected_to and isinstance(tail.connected_to.subject, UML.BehavioredClassifier)
        assert not head.connected_to or not tail.connected_to \
            or head.connected_to and tail.connected_to \
                and head.connected_to.subject != tail.connected_to.subject

        return can_connect

    def confirm_connect_handle (self, handle):
        """See RelationshipItem.confirm_connect_handle().
        """
        #print 'confirm_connect_handle', handle
        c1 = self.handles[0].connected_to
        c2 = self.handles[-1].connected_to
        if c1 and c2:
            s1 = c1.subject
            s2 = c2.subject
            relation = self.find_relationship(s1, s2)
            if not relation:
                relation = gaphor.resource(UML.ElementFactory).create(UML.Implementation)
                relation.general = s1
                relation.specific = s2
            self.subject = relation

    def confirm_disconnect_handle (self, handle, was_connected_to):
        """See RelationshipItem.confirm_disconnect_handle().
        """
        #print 'confirm_disconnect_handle', handle
        if self.subject:
            del self.subject

initialize_item(ImplementationItem, UML.Implementation)

