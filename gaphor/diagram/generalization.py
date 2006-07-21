'''
Generalization -- 
'''
# vim:sw=4

import gobject

from gaphor import resource
from gaphor import UML
from gaphor.diagram.diagramline import DiagramLine

class GeneralizationItem(DiagramLine):

    __uml__ = UML.Generalization
    __relationship__ = 'general', None, 'specific', 'generalization'

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)
        self.set(has_head=1, head_fill_color=0,
                 head_a=15.0, head_b=15.0, head_c=10.0, head_d=10.0)
        
    #
    # Gaphor Connection Protocol
    #

    def allow_connect_handle(self, handle, connecting_to):
        """See DiagramLine.allow_connect_handle().
        """
        try:
            if not connecting_to or not isinstance(connecting_to.subject, UML.Classifier):
                return False

            c1 = self.handles[0].connected_to
            c2 = self.handles[-1].connected_to
            if not c1 and not c2:
                return True
            if self.handles[0] is handle:
                h = self.handles[-1].connected_to
                return (h and h.subject is not connecting_to.subject)
            elif self.handles[-1] is handle:
                h = self.handles[0].connected_to
                return (h and h.subject is not connecting_to.subject)
            assert 0, 'Should never be reached...'
        except AttributeError, e:
            log.error('Generalization.allow_connect_handle: %s' % e, e)
            return False

    def confirm_connect_handle (self, handle):
        """See DiagramLine.confirm_connect_handle().
        """
        #print 'confirm_connect_handle', handle
        c1 = self.handles[0].connected_to
        c2 = self.handles[-1].connected_to
        if c1 and c2:
            s1 = c1.subject
            s2 = c2.subject
            relation = self.relationship
            if not relation:
                relation = resource(UML.ElementFactory).create(UML.Generalization)
                relation.general = s1
                relation.specific = s2
            self.subject = relation

    def confirm_disconnect_handle (self, handle, was_connected_to):
        """See DiagramLine.confirm_disconnect_handle().
        """
        self.set_subject(None)
