'''
CommentLine -- A line that connects a comment to another model element.
'''
# vim:sw=4

import gobject
import diacanvas
import gaphor.UML as UML
import relationship

class AssociationItem(relationship.RelationshipItem):

    def __init__(self):
	self.__super = super(AssociationItem, self)
	self.__super.__init__()
	self.end_head = None
	self.end_tail = None
	
    def save (self, store):
	self.__super.save(store)
	if self.end_head:
	    store.save_attribute('end_head', self.end_head)
	if self.end_tail:
	    store.save_attribute('end_tail', self.end_tail)

    def load (self, store):
	self.__super.load(store)
	try:
	    head_end = store.reference('head_end')
	    assert len(head_end) == 1
	    self._set_head_end(head_end[0])
	except ValueError:
	    pass
	try:
	    tail_end = store.reference('tail_end')
	    assert len(tail_end) == 1
	    self._set_tail_end(tail_end[0])
	except ValueError:
	    pass

    def do_set_property (self, pspec, value):
	if pspec.name == 'end_head':
	    self._set_end_head(value)
	elif pspec.name == 'end_tail':
	    self._set_end_tail(value)
	else:
	    self.__super.do_set_property(pspec, value)

    def do_get_property(self, pspec):
	if pspec.name == 'end_head':
	    return self.end_head
	elif pspec.name == 'end_tail':
	    return self.end_tail
	else:
	    return self.__super.do_get_property(pspec)

    def _set_end_head(self, end_head):
	if end_head is not self.end_head:
	    if self.end_head:
		self.end_head.remove_presentation(self)
	    self.end_head = end_head
	    if end_head:
		end_head.add_presentation(self)

    def _set_end_tail(self, end_tail):
	if end_tail is not self.end_tail:
	    if self.end_tail:
		self.end_tail.remove_presentation(self)
	    self.end_tail = end_tail
	    if end_tail:
		end_tail.add_presentation(self)

    def on_update (self, affine):
	self.__super.on_update(affine)

	#self.set(has_head=1, head_fill_color=0,
	#	 head_a=15.0, head_b=15.0, head_c=10.0, head_d=10.0)

    def on_parent_notify (self, parent):
	self.__super(parent);
        if self.end_head:
	    if self.parent:
		self.end_head.add_presentation (self)
	    else:
		self.end_head.remove_presentation (self)
        if self.end_tail:
	    if self.parent:
		self.end_tail.add_presentation (self)
	    else:
		self.end_tail.remove_presentation (self)

    # Gaphor Connection Protocol

    def find_relationship(self, head_subject, tail_subject):
	# Head and tail subjects are connected to an Association by 
	# AssociationEnds. 'end' is an association end
	for end_head in head_subject.association: # is AssociationEnd
	    assoc = end_head.association
	    if assoc:
		for end_tail in assoc.connection: 
		    if end_tail.participant is tail_subject and end_head is not end_tail:
			# check if this entry is not yet in the diagram
			# Return if the association is not (yet) on the canvas
			for item in assoc.presentations():
			    if item.canvas is self.canvas and item is not self:
				break
			else:
			    return end_head, end_tail, assoc
	return None, None, None

    def allow_connect_handle(self, handle, connecting_to):
	"""
	This method is called by a canvas item if the user tries to connect
	this object's handle. allow_connect_handle() checks if the line is
	allowed to be connected. In this case that means that one end of the
	line should be connected to a Comment.
	Returns: TRUE if connection is allowed, FALSE otherwise.
	"""
	try:
	    if not isinstance(connecting_to.subject, UML.Classifier):
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
	c1 = self.handles[0].connected_to
	c2 = self.handles[-1].connected_to
	if c1 and c2:
	    s1 = c1.subject
	    s2 = c2.subject
	    end_head, end_tail, relation = self.find_relationship(s1, s2)
	    if not relation:
		element_factory = GaphorResource(UML.ElementFactory)
		relation = element_factory.create(UML.Association)
		end_head = element_factory.create(UML.AssociationEnd)
		end_tail = element_factory.create(UML.AssociationEnd)
		relation.connection = end_head
		relation.connection = end_tail
		end_head.participant = s1
		end_tail.participant = s2
	    self._set_subject(relation)
	    self._set_end_head(end_head)
	    self._set_end_tail(end_tail)

    def confirm_disconnect_handle (self, handle, was_connected_to):
	if self.subject:
	    self._set_subject(None)
	    self._set_end_head(None)
	    self._set_end_tail(None)

gobject.type_register(AssociationItem)
