'''
AssociationItem -- Graphical representation of an association.
'''
# vim:sw=4

import gobject
import diacanvas
import gaphor.UML as UML
import relationship

class AssociationItem(relationship.RelationshipItem):
    """AssociationItem represents associations. 
    The associatonItem also has references to two AssociationEnd objects.
    Associations have text on both ends to represent multiplicity and
    the name of the association end. These texts will be kept in place
    by a constraint solver on object level.
    """

    def __init__(self):
	self.__super = super(AssociationItem, self)
	self.__super.__init__()

	self.head_end = None
	self.tail_end = None
	self.__solver = diacanvas.Solver()
	self.head_label = None
	self.head_mult = None
	self.tail_label = None
	self.tail_mult = None

    def save (self, store):
	self.__super.save(store)
	if self.head_end:
	    store.save_attribute('head_end', self.head_end)
	if self.tail_end:
	    store.save_attribute('tail_end', self.tail_end)

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
	if pspec.name == 'head_end':
	    self._set_head_end(value)
	elif pspec.name == 'tail_end':
	    self._set_tail_end(value)
	else:
	    self.__super.do_set_property(pspec, value)

    def do_get_property(self, pspec):
	if pspec.name == 'head_end':
	    return self.head_end
	elif pspec.name == 'tail_end':
	    return self.tail_end
	else:
	    return self.__super.do_get_property(pspec)

    def _set_head_end(self, head_end):
	if head_end is not self.head_end:
	    if self.head_end:
		self.head_end.remove_presentation(self)
	    self.head_end = head_end
	    if head_end:
		head_end.add_presentation(self)

    def _set_tail_end(self, tail_end):
	if tail_end is not self.tail_end:
	    if self.tail_end:
		self.tail_end.remove_presentation(self)
	    self.tail_end = tail_end
	    if tail_end:
		tail_end.add_presentation(self)

    def on_update (self, affine):
	self.__solver.resolve()
	self.__super.on_update(affine)

	#self.set(has_head=1, head_fill_color=0,
	#	 head_a=15.0, head_b=15.0, head_c=10.0, head_d=10.0)

    def on_parent_notify (self, parent):
	self.__super(parent);
        if self.head_end:
	    if self.parent:
		self.head_end.add_presentation (self)
	    else:
		self.head_end.remove_presentation (self)
        if self.tail_end:
	    if self.parent:
		self.tail_end.add_presentation (self)
	    else:
		self.tail_end.remove_presentation (self)

    # Gaphor Connection Protocol

    def find_relationship(self, head_subject, tail_subject):
	# Head and tail subjects are connected to an Association by 
	# AssociationEnds. 'end' is an association end
	for head_end in head_subject.association: # is AssociationEnd
	    assoc = head_end.association
	    if assoc:
		for tail_end in assoc.connection: 
		    if tail_end.participant is tail_subject and head_end is not tail_end:
			# check if this entry is not yet in the diagram
			# Return if the association is not (yet) on the canvas
			for item in assoc.presentations():
			    if item.canvas is self.canvas and item is not self:
				break
			else:
			    return head_end, tail_end, assoc
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
	    head_end, tail_end, relation = self.find_relationship(s1, s2)
	    if not relation:
		element_factory = GaphorResource(UML.ElementFactory)
		relation = element_factory.create(UML.Association)
		head_end = element_factory.create(UML.AssociationEnd)
		tail_end = element_factory.create(UML.AssociationEnd)
		relation.connection = head_end
		relation.connection = tail_end
		head_end.participant = s1
		tail_end.participant = s2
	    self._set_subject(relation)
	    self._set_head_end(head_end)
	    self._set_tail_end(tail_end)

    def confirm_disconnect_handle (self, handle, was_connected_to):
	if self.subject:
	    self._set_subject(None)
	    self._set_head_end(None)
	    self._set_tail_end(None)

gobject.type_register(AssociationItem)
