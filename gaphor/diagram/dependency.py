'''
Dependency -- 
'''
# vim:sw=4

import gobject
import diacanvas
import gaphor.UML as UML
import relationship

class DependencyItem(relationship.RelationshipItem):

    def __init__(self, id=None):
        relationship.RelationshipItem.__init__(self, id)
        self.set(dash=(7.0, 5.0), has_head=1, head_fill_color=0,
                 head_a=0.0, head_b=15.0, head_c=6.0, head_d=6.0)
        
    # Gaphor Connection Protocol

    def find_relationship(self, head_subject, tail_subject):
        """See RelationshipItem.find_relationship().
        """
        for supplier in head_subject.supplierDependency:
            #print 'supplier', supplier, supplier.client, tail_subject
            if tail_subject in supplier.client:
                # Check if the dependency is not already in our diagram
                for item in self.subject.presentation:
                    if item.canvas is self.canvas and item is not self:
                        break
                else:
                    return supplier

    def allow_connect_handle(self, handle, connecting_to):
        """See RelationshipItem.allow_connect_handle().
        """
        try:
            return isinstance(connecting_to.subject, UML.NamedElement)
        except AttributeError:
            return 0

    def confirm_connect_handle (self, handle):
        """See RelationshipItem.confirm_connect_handle().
        """
        #print 'confirm_connect_handle', handle, self.subject
        c1 = self.handles[0].connected_to
        c2 = self.handles[-1].connected_to
        if c1 and c2:
            s1 = c1.subject
            s2 = c2.subject
            relation = self.find_relationship(s1, s2)
            if not relation:
                relation = GaphorResource(UML.ElementFactory).create(UML.Dependency)
                relation.supplier = s1
                relation.client = s2
            self.subject = relation

    def confirm_disconnect_handle (self, handle, was_connected_to):
        """See RelationshipItem.confirm_disconnect_handle().
        """
        #print 'confirm_disconnect_handle', handle
        if self.subject:
            del self.subject

gobject.type_register(DependencyItem)
