'''
CommentLine -- A line that connects a comment to another model element.
'''
# vim:sw=4

import gobject
import diacanvas
import gaphor.UML as UML
import relationship

class GeneralizationItem(relationship.RelationshipItem):

    def __init__(self):
	relationship.RelationshipItem.__init__(self)
	self.set(has_head=1, head_fill_color=0,
		 head_a=15.0, head_b=15.0, head_c=10.0, head_d=10.0)
	
    # Gaphor Connection Protocol

    def find_relationship(self, head_subject, tail_subject):
	for rel in head_subject.specialization:
	    if rel.child is tail_subject:
		return rel

    def allow_connect_handle(self, handle, connecting_to):
	"""
	This method is called by a canvas item if the user tries to connect
	this object's handle. allow_connect_handle() checks if the line is
	allowed to be connected. In this case that means that one end of the
	line should be connected to a Comment.
	Returns: TRUE if connection is allowed, FALSE otherwise.
	"""
	try:
	    if not isinstance(connecting_to.subject, UML.GeneralizableElement):
		return 0

	    c1 = self.handles[0].connected_to
	    c2 = self.handles[-1].connected_to
	    if not c1 and not c2:
		return 1
	    if self.handles[0] is handle:
		return (self.handles[-1].connected_to.subject is not connecting_to.subject)
	    elif self.handles[-1] is handle:
		return (self.handles[0].connected_to.subject is not connecting_to.subject)
	    assert 1, 'Should never be reached...'
	except AttributeError:
	    return 0

    def confirm_connect_handle (self, handle):
	"""
	This method is called after a connection is established. This method
	sets the internal state of the line and updates the data model.
	"""
	print 'confirm_connect_handle', handle
	c1 = self.handles[0].connected_to
	c2 = self.handles[-1].connected_to
	if c1 and c2:
	    s1 = c1.subject
	    s2 = c2.subject
	    relation = self.find_relationship(s1, s2)
	    if not relation:
		relation = UML.ElementFactory().create(UML.Generalization)
		relation.parent = s1
		relation.child = s2
	    self._set_subject(relation)

    def confirm_disconnect_handle (self, handle, was_connected_to):
	print 'confirm_disconnect_handle', handle
	if self.subject:
	    self._set_subject(None)

gobject.type_register(GeneralizationItem)
