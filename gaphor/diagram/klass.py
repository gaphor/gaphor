'''
ClassItem diagram item
'''
# vim:sw=4

from modelelement import ModelElementItem
from feature import FeatureItem
import gaphor.UML as UML
import diacanvas
import gobject
import pango
from text import Text

class ClassItem(ModelElementItem):
    HEAD_MARGIN_X=60
    HEAD_MARGIN_Y=30
    NAME_FONT='sans bold 10'
    COMP_MARGIN_X=10
    COMP_MARGIN_Y=10

    def __init__(self):
	ModelElementItem.__init__(self)
	self.set(height=50, width=100)
	self.__attr_sep = diacanvas.shape.Path()
	self.__attr_sep.set_line_width(2.0)
	self.__oper_sep = diacanvas.shape.Path()
	self.__oper_sep.set_line_width(2.0)
	self.__border = diacanvas.shape.Path()
	self.__border.set_line_width(2.0)
	#self.__name = diacanvas.CanvasText()
	self.__name = Text()
	self.add_construction(self.__name)
	assert self.__name != None
	font = pango.FontDescription(ClassItem.NAME_FONT)
	self.__name.set(font=font, width=self.width, multiline=False,
			alignment=pango.ALIGN_CENTER)
	# Center the text:
	w, h = self.__name.get_property('layout').get_pixel_size()
	self.__name.move(0, (self.height - h) / 2)
	self.__name.set(height=h)
	self.__name.connect('text_changed', self.on_text_changed)

	# list of features:
	self.__attributes = list()
	self.__operations = list()

    def _set_subject(self, subject):
	ModelElementItem._set_subject(self, subject)
	self.__name.set(text=self.subject and self.subject.name or '')
	for f in subject.feature:
	    self._add_feature(f)
	self.request_update()

    def _add_feature(self, feature):
	"""Add a feature. The feature may be of class Attribute or
	Operation."""
	item = FeatureItem()
	item.set_property('subject', feature)
	item.set_property('parent', self)
	item.focus()
	log.debug('Feature added: %s' % item)

    def _remove_feature(self, feature):
	"""Remove a feature (Attribute or Operation)."""
	log.debug('Feature removing: %s' % item)
	for a in self.__attributes:
	    if a.subject is feature:
		self.remove(a)
		return True
	for o in self.__operations:
	    if o.subject is feature:
		self.remove(o)
		return True
	
    def on_update(self, affine):
	"""Overrides update callback."""
	width=0 #self.width
	height=ClassItem.HEAD_MARGIN_Y
	
	# Update class name
	layout = self.__name.get_property('layout')
	#layout.set_width(-1)
	w, h = layout.get_pixel_size()
	a = self.__name.get_property('affine')
	height += h
	aa = (a[0], a[1], a[2], a[3], a[4], height / 2)
	# aa = a[0:4] + (height /2,) seems to crash...
	self.__name.set(affine=aa, height=h)
	
	width = max(width, w + ClassItem.HEAD_MARGIN_X)
	attr_sep_y = height
	height += ClassItem.COMP_MARGIN_Y

	# handle attributes:
	for attr in self.__attributes:
	    layout = attr.get_property('layout')
	    layout.set_width(-1)
	    w, h = layout.get_pixel_size()
	    a = attr.get_property('affine')
	    aa = (a[0], a[1], a[2], a[3], ClassItem.COMP_MARGIN_X, height)
	    height += h
	    #aa = a[0:4] + (height,)
	    attr.set(affine=aa, height=h, width=w)
	    width = max(width, w + 2 * ClassItem.COMP_MARGIN_X)

	height += ClassItem.COMP_MARGIN_Y
	oper_sep_y = height
	height += ClassItem.COMP_MARGIN_Y

	# handle operations:
	for oper in self.__operations:
	    layout = oper.get_property('layout')
	    layout.set_width(-1)
	    w, h = layout.get_pixel_size()
	    a = oper.get_property('affine')
	    aa = (a[0], a[1], a[2], a[3], ClassItem.COMP_MARGIN_X, height)
	    height += h
#	    aa = a[0:4] + (height,)
	    oper.set(affine=aa, height=h, width=w)
	    width = max(width, w + 2 * ClassItem.COMP_MARGIN_X)

	height += ClassItem.COMP_MARGIN_Y
	width = max(width, self.width)

	# We know the width of all text components and set it:
	self.__name.set(width=width)
	self.set(min_width=width, min_height=height)
	self.update_child(self.__name, affine)
	for attr in self.__attributes:
	    self.update_child(attr, affine)
	for oper in self.__operations:
	    self.update_child(oper, affine)
	ModelElementItem.on_update(self, affine)
	self.__attr_sep.line(((0, attr_sep_y), (width, attr_sep_y)))
	self.__oper_sep.line(((0, oper_sep_y), (width, oper_sep_y)))
	self.__border.rectangle((0,0),(width, height))
	self.expand_bounds(1.0)

    def on_event (self, event):
	if event.type == diacanvas.EVENT_KEY_PRESS:
	    self.__name.focus()
	    self.__name.on_event (event)
	    return True
	else:
	    return ModelElementItem.on_event(self, event)

    def on_get_shape_iter(self):
	return self.__border

    def on_shape_next(self, iter):
	if iter is self.__border:
	    return self.__attr_sep
	if iter is self.__attr_sep:
	    return self.__oper_sep
	return None

    def on_shape_value(self, iter):
	return iter

    # Groupable

    def on_groupable_add(self, item):
	"""Add an attribute or operation."""
	if isinstance(item.subject, UML.Attribute):
	    self.__attributes.append(item)
	    item.focus()
	    return 1
	elif isinstance(item.subject, UML.Operation):
	    self.__operations.append(item)
	    item.focus()
	    return 1
	return 0

    def on_groupable_remove(self, item):
	"""Remove a feature subitem."""
	if item in self.__attributes:
	    self.__attributes.remove(item)
	    log.debug('Attribute removed: %s' % item)
	    return 1
	elif item in self.__operations:
	    self.__operations.remove(item)
	    log.debug('Operation removed: %s' % item)
	    return 1
	return 0

    def on_groupable_get_iter(self):
	return self.__name

    def on_groupable_next(self, iter):
	"""Iterate over the class' name, its attributes and the operations."""
	if iter is self.__name:
	    if self.__attributes:
		return self.__attributes[0]
	    elif self.__operations:
		return self.__operations[0]
	elif iter in self.__attributes and not iter is self.__attributes[-1]:
	    return self.__attributes[self.__attributes.index(iter) + 1]
	elif iter is self.__attributes[-1] and self.__operations:
	    return self.__operations[0]
	elif iter in self.__operations and not iter is self.__operations[-1]:
	    return self.__operations[self.__operations.index(iter) + 1]
	else:
	    return None

    def on_groupable_value(self, iter):
	return iter

    def on_groupable_length(self):
	return 1 + len(self.__attributes) + len(self.__operations)

    def on_groupable_pos(self, item):
	if item == self.__name:
	    return 0
	elif item in self.__attributes:
	    return self.__attributes.index(item) + 1
	elif item in self.__operations:
	    return self.__operations.index(item) + len(self.__attributes) + 1
	else:
	    return -1

    def on_subject_update(self, name, old_value, new_value):
	"""Update self when the subject changes."""
	if name == '__unlink__':
	    for a in self.__attributes + self.__operations:
		self.remove(a)
		#a.set_property('subject', None)
	    assert len(self.__attributes) == 0
	    assert len(self.__operations) == 0
	    ModelElementItem.on_subject_update(self, name, old_value, new_value)
	elif name == 'name':
	    self.__name.set(text=self.subject.name)
	elif name == 'feature' and (self.canvas and not self.canvas.in_undo):
	    # Only hande the feature if we're part of a diagram
	    log.debug('New feature: %s' % str(new_value))
	    if old_value == 'add':
		self._add_feature(new_value)
	    elif old_value == 'remove':
		self._remove_feature(new_value)
	else:
	    ModelElementItem.on_subject_update(self, name, old_value, new_value)

    def on_text_changed(self, text_item, text):
	if text != self.subject.name:
	    self.subject.name = text

gobject.type_register(ClassItem)

