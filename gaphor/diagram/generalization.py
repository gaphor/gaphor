'''
Generalization -- 
'''
# vim:sw=4

import gobject
import diacanvas
import gaphor
import gaphor.UML as UML
from gaphor.diagram import initialize_item
import relationship

class GeneralizationItem(relationship.RelationshipItem):

    def __init__(self, id=None):
        relationship.RelationshipItem.__init__(self, id)
        self.set(has_head=1, head_fill_color=0,
                 head_a=15.0, head_b=15.0, head_c=10.0, head_d=10.0)
        
    # Gaphor Connection Protocol

    def find_relationship(self, head_subject, tail_subject):
        """See RelationshipItem.find_relationship().
        """
	if self.subject and \
	   self.subject.general is head_subject and \
	   self.subject.specific is tail_subject:
	    return self.subject

        for gen in tail_subject.generalization:
            if gen.general is head_subject:
                # check for this entry on self.canvas
                for item in spec.subject.presentation:
                    # Allow self to be returned. Avoids strange
                    # behaviour during loading
                    if item.canvas is self.canvas and item is not self:
                        break
                else:
                    return spec
        return None

    def allow_connect_handle(self, handle, connecting_to):
        """See RelationshipItem.allow_connect_handle().
        """
        try:
            if not isinstance(connecting_to.subject, UML.Classifier):
                return False

            c1 = self.handles[0].connected_to
            c2 = self.handles[-1].connected_to
            if not c1 and not c2:
                return True
            if self.handles[0] is handle:
                return (self.handles[-1].connected_to.subject is not connecting_to.subject)
            elif self.handles[-1] is handle:
                return (self.handles[0].connected_to.subject is not connecting_to.subject)
            assert 1, 'Should never be reached...'
        except AttributeError, e:
            log.debug('Generalization.allow_connect_handle: %s' % e)
            return False

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
                relation = gaphor.resource(UML.ElementFactory).create(UML.Generalization)
                relation.general = s1
                relation.specific = s2
            self.subject = relation

    def confirm_disconnect_handle (self, handle, was_connected_to):
        """See RelationshipItem.confirm_disconnect_handle().
        """
        #print 'confirm_disconnect_handle', handle
        if self.subject:
            del self.subject

initialize_item(GeneralizationItem, UML.Generalization)
