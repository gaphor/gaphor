'''
AssociationItem -- Graphical representation of an association.
'''
# vim:sw=4

import gobject
import diacanvas
import pango
import gaphor.UML as UML
from relationship import RelationshipItem
from diacanvas import CanvasText

class AssociationItem(RelationshipItem, diacanvas.CanvasAbstractGroup):
    """AssociationItem represents associations. 
    The associatonItem also has references to two AssociationEnd objects.
    Associations have text on both ends to represent multiplicity and
    the name of the association end. These texts will be kept in place
    by a constraint solver on object level.
    """
    
    def __init__(self):
	RelationshipItem.__init__(self)

	self.head_end = None
	self.tail_end = None

	self.__head_name = AssociationLabel('name')
	self.add_construction(self.__head_name)
	self.__head_name.connect('text-changed',
				 self.on_association_end_text_changed)
	self.__head_mult = AssociationLabel('multiplicity')
	self.add_construction(self.__head_mult)
	self.__head_mult.connect('text-changed',
				 self.on_association_end_text_changed)
	self.__tail_name = AssociationLabel('name')
	self.add_construction(self.__tail_name)
	self.__tail_name.connect('text-changed',
				 self.on_association_end_text_changed)
	self.__tail_mult = AssociationLabel('multiplicity')
	self.add_construction(self.__tail_mult)
	self.__tail_mult.connect('text-changed',
				 self.on_association_end_text_changed)

    def save (self, save_func):
	RelationshipItem.save(self, save_func)
	if self.head_end:
	    save_func('head_end', self.head_end)
	if self.tail_end:
	    save_func('tail_end', self.tail_end)

    def load (self, name, value):
	# end_head and end_tail were used in an older Gaphor version
	if name in ( 'head_end', 'end_head' ):
	    self._set_head_end(value)
	elif name in ( 'tail_end', 'end_tail' ):
	    self._set_tail_end(value)
	else:
	    RelationshipItem.load(self, name, value)

    def do_set_property (self, pspec, value):
	if pspec.name == 'head_end':
	    self._set_head_end(value)
	elif pspec.name == 'tail_end':
	    self._set_tail_end(value)
	else:
	    RelationshipItem.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
	if pspec.name == 'head_end':
	    return self.head_end
	elif pspec.name == 'tail_end':
	    return self.tail_end
	else:
	    #print 'Association.__dict__ =', self.__dict__
	    return RelationshipItem.do_get_property(self, pspec)

    def has_capability(self, capability):
	if capability == 'head_is_navigable':
	    return self.head_end and self.head_end.isNavigable or False
	elif capability == 'tail_is_navigable':
	    return self.tail_end and self.tail_end.isNavigable or False
	elif capability == 'head_ak_none':
	    return self.head_end and (self.head_end.aggregation == UML.AK_NONE) or False
	elif capability == 'head_ak_aggregate':
	    return self.head_end and (self.head_end.aggregation == UML.AK_AGGREGATE) or False
	elif capability == 'head_ak_composite':
	    return self.head_end and (self.head_end.aggregation == UML.AK_COMPOSITE) or False
	elif capability == 'tail_ak_none':
	    return self.tail_end and (self.tail_end.aggregation == UML.AK_NONE) or False
	elif capability == 'tail_ak_aggregate':
	    return self.tail_end and (self.tail_end.aggregation == UML.AK_AGGREGATE) or False
	elif capability == 'tail_ak_composite':
	    return self.tail_end and (self.tail_end.aggregation == UML.AK_COMPOSITE) or False
	else:
	    return RelationshipItem.has_capability(self, capability)

    def _set_head_end(self, head_end):
	if head_end is not self.head_end:
	    if self.head_end:
		self.head_end.disconnect(self.on_association_end_update)
		self.head_end.remove_presentation(self)
	    self.head_end = head_end
	    if head_end:
		head_end.add_presentation(self)
		self.head_end.connect(self.on_association_end_update, head_end)
		self.__head_name.set_property('text', head_end.name)
		self.__head_mult.set_property('text', head_end.multiplicity)

    def _set_tail_end(self, tail_end):
	if tail_end is not self.tail_end:
	    if self.tail_end:
		self.tail_end.disconnect(self.on_association_end_update)
		self.tail_end.remove_presentation(self)
	    self.tail_end = tail_end
	    if tail_end:
		tail_end.add_presentation(self)
		self.tail_end.connect(self.on_association_end_update, tail_end)
		self.__tail_name.set_property('text', tail_end.name)
		self.__tail_mult.set_property('text', tail_end.multiplicity)

    def __update_labels(self, name_label, mult_label, p1, p2):
	"""Update label placement for association's name and
	multiplicity label. p1 is the line end and p2 is the last
	but one point of the line."""
	ofs = 5

	name_dx = 0.0
	name_dy = 0.0
	mult_dx = 0.0
	mult_dy = 0.0

	dx = float(p2[0]) - float(p1[0])
	dy = float(p2[1]) - float(p1[1])
	
	if dy == 0:
	    rc = 1000.0 # quite a lot...
	else:
	    rc = dx / dy
	abs_rc = abs(rc)
	h = dx > 0 # right side of the box
	v = dy > 0 # bottom side

	layout = name_label.get_property('layout')
	name_w, name_h = layout.get_pixel_size()

	layout = mult_label.get_property('layout')
	mult_w, mult_h = layout.get_pixel_size()

	if abs_rc > 6:
	    #print 'horizontal line'
	    if h:
		name_dx = ofs
		name_dy = -ofs - name_h # - height
		mult_dx = ofs
		mult_dy = ofs
	    else:
		name_dx = -ofs - name_w
		name_dy = -ofs - name_h # - height
		mult_dx = -ofs - mult_w
		mult_dy = ofs
	elif 0 <= abs_rc <= 0.2:
	    #print 'vertical line'
	    if v:
		name_dx = -ofs - name_w # - width
		name_dy = ofs
		mult_dx = ofs
		mult_dy = ofs
	    else:
		name_dx = -ofs - name_w # - width
		name_dy = -ofs - name_h # - height
		mult_dx = ofs
		mult_dy = -ofs - mult_h # - height
	else:
	    r = abs_rc < 1.0
	    align_left = (h and not r) or (r and not h)
	    align_bottom = (v and not r) or (r and not v)
	    if align_left:
		name_dx = ofs
		mult_dx = ofs
	    else:
		name_dx = -ofs - name_w # - width
		mult_dx = -ofs - mult_w # - width
	    if align_bottom:
		name_dy = -ofs - name_h # - height
		mult_dy = -ofs - name_h - mult_h # - height
	    else:
		name_dy = ofs 
		mult_dy = ofs + mult_h # + height
	a = name_label.get_property('affine')
	name_label.set_property('affine', a[:4] + (p1[0] + name_dx, p1[1] + name_dy))
	name_label.set(width=name_w, height=name_h)
	a = mult_label.get_property('affine')
	mult_label.set_property('affine', a[:4] + (p1[0] + mult_dx, p1[1] + mult_dy))
	mult_label.set(width=mult_w, height=mult_h)

    def on_update (self, affine):
	"""Update the shapes and sub-items of the association."""
	# Update line endings:
	if self.head_end and self.tail_end:
	    # Update line ends using the aggregation and isNavigable values:
	    self.set(has_tail=0, has_head=0)

	    if self.head_end.aggregation == UML.AK_NONE:
	       if self.head_end.isNavigable and not self.tail_end.isNavigable:
		    self.set(has_head=1,
			     head_a=0.0, head_b=15.0, head_c=6.0, head_d=6.0)
	    else:
		self.set(has_head=1, head_a=20, head_b=10, head_c=6, head_d=6)
		if self.head_end.aggregation == UML.AK_COMPOSITE:
		    self.set(head_fill_color=diacanvas.color(0,0,0,255))
		else:
		    self.set(head_fill_color=diacanvas.color(0,0,0,0))

	    if self.tail_end.aggregation == UML.AK_NONE:
	       if self.tail_end.isNavigable and not self.head_end.isNavigable:
		    self.set(has_tail=1,
			     tail_a=0.0, tail_b=15.0, tail_c=6.0, tail_d=6.0)
	    else:
		self.set(has_tail=1, tail_a=20, tail_b=10, tail_c=6, tail_d=6)
		if self.tail_end.aggregation == UML.AK_COMPOSITE:
		    self.set(tail_fill_color=diacanvas.color(0,0,0,255))
		else:
		    self.set(tail_fill_color=diacanvas.color(0,0,0,0))
		    
	RelationshipItem.on_update(self, affine)

	handles = self.handles
	# Calculate alignment of the head name and multiplicity
	self.__update_labels(self.__head_name, self.__head_mult,
			     handles[0].get_pos_i(), handles[1].get_pos_i())

	# Calculate alignment of the tail name and multiplicity
	self.__update_labels(self.__tail_name, self.__tail_mult,
			     handles[-1].get_pos_i(), handles[-2].get_pos_i())
	
	self.update_child(self.__head_name, affine)
	self.update_child(self.__head_mult, affine)
	self.update_child(self.__tail_name, affine)
	self.update_child(self.__tail_mult, affine)

	# bounds calculation
	b1 = self.bounds
	b2 = self.__head_name.get_bounds(self.__head_name.affine)
	b3 = self.__head_mult.get_bounds(self.__head_mult.affine)
	b4 = self.__tail_name.get_bounds(self.__tail_name.affine)
	b5 = self.__tail_mult.get_bounds(self.__tail_mult.affine)
	new_bounds = (min(b1[0], b2[0], b3[0], b4[0], b5[0]),
		      min(b1[1], b2[1], b3[1], b4[1], b5[1]),
		      max(b1[2], b2[2], b3[2], b4[2], b5[2]),
		      max(b1[3], b2[3], b3[3], b4[3], b5[3]))
	self.set_bounds(new_bounds)
		    
    def on_parent_notify (self, parent):
	RelationshipItem.on_parent_notify(self, parent);
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
    
    def on_association_end_update(self, name, old_value, new_value, end):
	if name in ('aggregation', 'isNavigable'):
	    self.request_update()
	elif name == 'name':
	    if end is self.head_end:
		self.__head_name.set_property('text', new_value)
	    elif end is self.tail_end:
		self.__tail_name.set_property('text', new_value)
	elif name == 'multiplicity':
	    if end is self.head_end:
		self.__head_mult.set_property('text', new_value)
	    elif end is self.tail_end:
		self.__tail_mult.set_property('text', new_value)

    def on_association_end_text_changed(self, label, text):
	# Do not try to set text, if there's no association.
	if not self.subject:
	    return
	if label is self.__head_name:
	    if self.head_end.name != text:
		self.head_end.name = text
	elif label is self.__head_mult:
	    if self.head_end.multiplicity != text:
		self.head_end.multiplicity = text
	elif label is self.__tail_name:
	    if self.tail_end.name != text:
		self.tail_end.name = text
	elif label is self.__tail_mult:
	    if self.tail_end.multiplicity != text:
		self.tail_end.multiplicity = text

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

	    return 1
	    # Also allow connections to the same class...
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
		# copy text from ends to AssociationEnds:
		head_end.name = self.__head_name.get_property('text')
		head_end.multiplicity = self.__head_mult.get_property('text')
		tail_end.name = self.__tail_name.get_property('text')
		tail_end.multiplicity = self.__tail_mult.get_property('text')
	    self._set_subject(relation)
	    self._set_head_end(head_end)
	    self._set_tail_end(tail_end)

    def confirm_disconnect_handle (self, handle, was_connected_to):
	if self.subject:
	    self._set_subject(None)
	    self._set_head_end(None)
	    self._set_tail_end(None)

    # Groupable

    def on_groupable_add(self, item):
	return 0

    def on_groupable_remove(self, item):
	'''Do not allow the name to be removed.'''
	#self.emit_stop_by_name('remove')
	##return 0
	return 1

    def on_groupable_get_iter(self):
	return self.__head_name

    def on_groupable_next(self, iter):
	if iter is self.__head_name:
	    return self.__head_mult
	elif iter is self.__head_mult:
	    return self.__tail_name
	elif iter is self.__tail_name:
	    return self.__tail_mult
	return None

    def on_groupable_value(self, iter):
	return iter

    def on_groupable_length(self):
	return 4

    def on_groupable_pos(self, item):
	if item is self.__head_name:
	    return 0
	elif item is self.__head_mult:
	    return 1
	elif item is self.__tail_name:
	    return 2
	elif item is self.__tail_mult:
	    return 3
	return -1

class AssociationLabel(CanvasText):
    """This is a label that is placed on the end of an association.
    The label has a minimum width of 10 and shows a rectangle around then
    the association is selected.
    """
    LABEL_FONT='sans 10'

    def __init__(self, name):
	self.__gobject_init__()
	# don't call CanvasText.__init__(self), it will screw up the callbacks
	self.name = name
	font = pango.FontDescription(AssociationLabel.LABEL_FONT)
	self.set(font=font, multiline=False)
	self.__border = diacanvas.shape.Path()
	self.__border.set_color(diacanvas.color(128,128,128))
	self.__border.set_line_width(1.0)
	self.__border.set_visibility(diacanvas.shape.SHAPE_VISIBLE_IF_SELECTED)

    def on_update(self, affine):
	# Set a minimun width, so we can always select it
	w, h = self.get_property('layout').get_pixel_size()
	self.set_property('width', max(w, 10.0))

	CanvasText.on_update(self, affine)
	x1, y1, x2, y2 = self.get_bounds()
	self.__border.rectangle((x1 + 0.5, y1 + 0.5), (x2 - 0.5, y2 - 0.5))

    def on_event(self, event):
	if event.type == diacanvas.EVENT_BUTTON_PRESS:
	    log.info('Edit Association ends %s' % self.name)
	return CanvasText.on_event(self, event)

    def on_get_shape_iter(self):
	return self.__border

    def on_shape_next(self, iter):
	if iter is self.__border:
	    return CanvasText.on_get_shape_iter(self)
	else:
	    return CanvasText.on_shape_next(self, iter)

    def on_shape_value(self, iter):
	if iter is self.__border:
	    return iter
	else:
	    return CanvasText.on_shape_value(self, iter)

gobject.type_register(AssociationItem)
diacanvas.set_groupable(AssociationItem)
gobject.type_register(AssociationLabel)
diacanvas.set_callbacks(AssociationLabel)

