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
#from text import Text


class Compartment(object):
    """Specify a compartment in a class item."""

    def __init__(self, func):
	self.func = func
	self.visible = True


class ClassItem(ModelElementItem):
    __gproperties__ = {
	'show-attributes': (gobject.TYPE_BOOLEAN, 'show attributes',
			    '',
			    1, gobject.PARAM_READWRITE),
	'show-operations': (gobject.TYPE_BOOLEAN, 'show operations',
			    '',
			    1, gobject.PARAM_READWRITE),
    }
    HEAD_MARGIN_X=30
    HEAD_MARGIN_Y=10
    NAME_FONT='sans bold 10'
    COMP_MARGIN_X=5
    COMP_MARGIN_Y=5

    def __init__(self):
	ModelElementItem.__init__(self)
	self.set(height=50, width=100)
	self.__attr_sep = diacanvas.shape.Path()
	self.__attr_sep.set_line_width(2.0)
	self.__oper_sep = diacanvas.shape.Path()
	self.__oper_sep.set_line_width(2.0)
	self.__border = diacanvas.shape.Path()
	self.__border.set_line_width(2.0)
	self.__name = diacanvas.CanvasText()
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

	# list of features, both attributes and operations:
	self.__features = list()

	# For now, we have two defined compartments, one for attributes and
	# one for operations.
	self.__compartments = [
	    Compartment(lambda e: e.subject.isKindOf(UML.Attribute)),
	    Compartment(lambda e: e.subject.isKindOf(UML.Operation))
	]

    def save(self, save_func):
	# Store the show- properties *before* the width/height properties,
	# otherwise the classes will unintentionally grow due to "visible"
	# attributes or operations.
	self.save_property(save_func, 'show-attributes')
	self.save_property(save_func, 'show-operations')
	ModelElementItem.save(self, save_func)

    def do_set_property(self, pspec, value):
	if pspec.name == 'show-attributes':
	    self.preserve_property('show-attributes')
	    self.__compartments[0].visible = value
	    self.request_update()
	elif pspec.name == 'show-operations':
	    self.preserve_property('show-operations')
	    self.__compartments[1].visible = value
	    self.request_update()
	else:
	    ModelElementItem.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
	if pspec.name == 'show-attributes':
	    return self.__compartments[0].visible
	elif pspec.name == 'show-operations':
	    return self.__compartments[1].visible
	return ModelElementItem.do_get_property(self, pspec)

    def has_capability(self, capability):
	log.debug('has_capability: %s' % capability)
	if capability == 'show-attributes':
	    return self.__compartments[0].visible
	elif capability == 'show-operations':
	    return self.__compartments[1].visible
	return ModelElementItem.has_capability(self, capability)

    def _set_subject(self, subject):
	ModelElementItem._set_subject(self, subject)
	self.__name.set(text=self.subject and self.subject.name or '')
	for f in subject.feature:
	    self._add_feature(f)
	self.request_update()

    def _add_feature(self, feature):
	"""Add a feature. The feature may be of class Attribute or
	Operation."""
	#try:
	#    log.debug('Adding feature for class %s: %s' % (self.subject.name, feature.name))
	#except:
	#    pass
	# We have to ensure an item has not yet been added for the feature,
	# somehow featureItems doubled when loaded from a file...
	for f in self.__features:
	    if f.subject is feature:
		return
	item = FeatureItem()
	item.set_property('subject', feature)
	self.add(item)
	self._update_features()
	item.focus()

    def _remove_feature(self, feature):
	"""Remove a feature (Attribute or Operation)."""
	#try:
	#    log.debug('Removing feature for class %s: %s' % (self.subject.name, feature.name))
	#except:
	#    pass
	for f in self.__features:
	    if f.subject is feature:
		self.remove(f)
		self._update_features()
		return True
	
    def _update_features(self):
	"""Update a list of features (attributes or operations) and return
	the max width and the new y coordinate."""
	self.on_update(None)

    def on_update(self, affine):
	"""Overrides update callback. If affine is None, it is called just for
	updating the item width and height."""
	width = 0
	height = ClassItem.HEAD_MARGIN_Y
	sep_y = list()

	# TODO: update stereotype

	# Update class name
	layout = self.__name.get_property('layout')
	w, h = layout.get_pixel_size()
	height += h
	if affine:
	    a = self.__name.get_property('affine')
	    a = (a[0], a[1], a[2], a[3], a[4], height / 2)
	    self.__name.set(affine=a, height=h)
	
	height += ClassItem.HEAD_MARGIN_Y
	width = w + ClassItem.HEAD_MARGIN_X

	# Update feature list
	for comp in self.__compartments:
	    if comp.visible:
		sep_y.append(height)
		height += ClassItem.COMP_MARGIN_Y
		for f in filter(comp.func, self.__features):
		    layout = f.get_property('layout')
		    w, h = layout.get_pixel_size()
		    if affine:
			a = f.get_property('affine')
			a = (a[0], a[1], a[2], a[3], ClassItem.COMP_MARGIN_X, height)
			f.set(affine=a, height=h, width=w, visible=1)
		    height += h
		    width = max(width, w + 2 * ClassItem.COMP_MARGIN_X)

		height += ClassItem.COMP_MARGIN_Y
	    else:
		for f in filter(comp.func, self.__features):
		    f.set(visible=0)

	self.set(min_width=width, min_height=height)

	if affine:
	    width = max(width, self.width)
	    height = max(height, self.height)

	    # We know the width of all text components and set it:
	    self.__name.set(width=width)
	    self.update_child(self.__name, affine)
	    for f in self.__features:
		self.update_child(f, affine)
	    ModelElementItem.on_update(self, affine)

	    i = 0
	    if self.__compartments[0].visible:
		self.__attr_sep.line(((0, sep_y[i]), (width, sep_y[i])))
		i += 1
	    if self.__compartments[1].visible:
		self.__oper_sep.line(((0, sep_y[i]), (width, sep_y[i])))

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
	    if self.__compartments[0].visible:
		return self.__attr_sep
	    iter = self.__attr_sep # Fall through
	if iter is self.__attr_sep:
	    if self.__compartments[1].visible:
		return self.__oper_sep
	return None

    def on_shape_value(self, iter):
	return iter

    # Groupable

    def on_groupable_add(self, item):
	"""Add an attribute or operation."""
	if isinstance(item.subject, UML.Feature):
	    #log.debug('Adding feature %s' % item)
	    self.__features.append(item)
	    return 1
	else:
	    log.warning('feature %s is not a Feature' % item)
	return 0

    def on_groupable_remove(self, item):
	"""Remove a feature subitem."""
	if item in self.__features:
	    self.__features.remove(item)
	    #log.debug('Feature removed: %s' % item)
	    return 1
	else:
	    log.warning('feature %s not found in feature list' % item)
	return 0

    def on_groupable_get_iter(self):
	return self.__name

    def on_groupable_next(self, iter):
	"""Iterate over the class' name, its attributes and the operations."""
	if iter is self.__name:
	    if self.__features:
		return self.__features[0]
	    else:
		return None
	elif iter in self.__features and not iter is self.__features[-1]:
	    return self.__features[self.__features.index(iter) + 1]
	else:
	    return None

    def on_groupable_value(self, iter):
	return iter

    def on_groupable_length(self):
	return 1 + len(self.__features)

    def on_groupable_pos(self, item):
	if item == self.__name:
	    return 0
	elif item in self.__features:
	    return 1 + self.__features.index(item)
	else:
	    return -1

    def on_subject_update(self, name, old_value, new_value):
	"""Update self when the subject changes."""
	if name == '__unlink__':
	    for f in self.__features:
		f.set_subject(None)
	    #assert len(self.__features) == 0, '%d features still exist' % len(self.__features)
	    ModelElementItem.on_subject_update(self, name, old_value, new_value)
	elif name == 'name':
	    self.__name.set(text=self.subject.name)
	elif name == 'feature' and (self.canvas and not self.canvas.in_undo):
	    # Only hande the feature if we're part of a diagram
	    #log.debug('on_subject_update(%s, %s)' % (old_value, new_value))
	    if old_value == 'add':
		self._add_feature(new_value)
	    elif old_value == 'remove':
		self._remove_feature(new_value)
	else:
	    ModelElementItem.on_subject_update(self, name, old_value, new_value)

    def on_text_changed(self, text_item, text):
	if text != self.subject.name:
	    self.subject.name = text
	self._update_features()

gobject.type_register(ClassItem)

