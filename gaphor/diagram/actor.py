'''
ActorItem diagram item
'''
# vim:sw=4

from modelelement import ModelElementItem
import diacanvas
import pango
import gobject
import sys

class ActorItem(ModelElementItem):
    __gsignals__ = { 'need_update': 'override' }
    HEAD=11
    ARM=19
    NECK=10
    BODY=20
    FONT='sans bold 10'

    __gproperties__ = {
	'name-width':	(gobject.TYPE_DOUBLE, 'name width',
			 '', 0.0, 10000.0,
			 1, gobject.PARAM_READWRITE),
    }
    def __init__(self):
	#assert sys.getrefcount(self) == 5, sys.getrefcount(self)
	ModelElementItem.__init__(self)
	#assert sys.getrefcount(self) == 6, sys.getrefcount(self)
	self.set(height=(ActorItem.HEAD + ActorItem.NECK + ActorItem.BODY + ActorItem.ARM),
		 width=(ActorItem.ARM * 2))
	self.set(min_height=(ActorItem.HEAD + ActorItem.NECK + ActorItem.BODY + ActorItem.ARM),
		 min_width=(ActorItem.ARM * 2))
	# Head
	self.__head = diacanvas.shape.Ellipse()
	self.__head.set_line_width(2.0)
	# Body
	self.__body = diacanvas.shape.Path()
	self.__body.set_line_width(2.0)
	# Arm
	self.__arms = diacanvas.shape.Path()
	self.__arms.set_line_width(2.0)
	# Legs
	self.__legs = diacanvas.shape.Path()
	self.__legs.set_line_width(2.0)
	# Name
	self.__name = diacanvas.CanvasText()
	self.add_construction(self.__name)
	assert self.__name != None
	font = pango.FontDescription(ActorItem.FONT)
	self.__name.set(font=font,
			alignment=pango.ALIGN_CENTER)
	self.__name_update()
	#assert sys.getrefcount(self) == 6, sys.getrefcount(self)
	# Hack since self.<method> is not GC'ed
	def on_text_changed(text_item, text, actor):
	    if text != actor.subject.name:
		actor.subject.name = text
		actor.__name_update()
	#self.__name.connect('text_changed', self.on_text_changed)
	# This statement makes it crash... Seems like python and signals do
	# not get along very well...
	self.__name.connect('text_changed', on_text_changed, self)
	#assert sys.getrefcount(self) == 7, sys.getrefcount(self)

    def do_set_property (self, pspec, value):
	print 'Actor: Trying to set property', pspec.name, value
	if pspec.name == 'name-width':
	    self.__name.set_property('width', value)
	else:
	    ModelElementItem.do_set_property (self, pspec, value)

    def do_get_property(self, pspec):
	if pspec.name == 'name-width':
	    return self.__name.get_property('width')
	else:
	    return ModelElementItem.do_get_property (self, pspec)

    def __name_update (self):
	'''Center the name text under the actor.'''
	w, h = self.__name.get_property('layout').get_pixel_size()
	#print 'ActorItem:',w,h, self.__name.get_property('text')
	#self.set(min_width=w + UseCase.MARGIN_X,
	#	 min_height=h + UseCase.MARGIN_Y)
	a = self.__name.get_property('affine')
	if w < self.width:
	    w = self.width
	aa = (a[0], a[1], a[2], a[3], (self.width - w) / 2, self.height)
	#self.__name.set(affine=aa, width=self.width, height=h)
	self.__name.set(affine=aa, width=w, height=h)
	#print 'Actor:', w, h, self.width, self.height, aa[4], aa[5]

    def save (self, store):
	ModelElementItem.save(self, store)
	store.save_property('name-width')

    def load(self, store):
	ModelElementItem.load(self, store)
	self.set_property('name-width', eval (store.value('name-width')))
	#self.__name_update()

    def do_need_update(self):
	self.__name.request_update()

    def on_update(self, affine):
	ModelElementItem.on_update(self, affine)

	# scaling factors (also compenate the line width):
	fx = self.width / (ActorItem.ARM * 2 + 2);
	fy = self.height / (ActorItem.HEAD + ActorItem.NECK + ActorItem.BODY + ActorItem.ARM + 2);
	self.__head.ellipse((ActorItem.ARM * fx, (ActorItem.HEAD / 2) * fy),
			    ActorItem.HEAD * fx, ActorItem.HEAD * fy)
	self.__head.request_update()
	self.__body.line(((ActorItem.ARM * fx, ActorItem.HEAD * fy),
			 (ActorItem.ARM * fx, (ActorItem.HEAD + ActorItem.NECK + ActorItem.BODY) * fy)))
	self.__body.request_update()
	self.__arms.line(((0, (ActorItem.HEAD + ActorItem.NECK) * fy),
			 (ActorItem.ARM * 2 * fx, (ActorItem.HEAD + ActorItem.NECK) * fy)))
	self.__arms.request_update()
	self.__legs.line(((0, (ActorItem.HEAD + ActorItem.NECK + ActorItem.BODY + ActorItem.ARM) * fy),
			  (ActorItem.ARM * fx, (ActorItem.HEAD + ActorItem.NECK + ActorItem.BODY) * fy),
			  (ActorItem.ARM * 2 * fx, (ActorItem.HEAD + ActorItem.NECK + ActorItem.BODY + ActorItem.ARM) * fy)))
	self.__legs.request_update()
	self.update_child(self.__name, affine)
	# Update the bounding box:
	ulx, uly, lrx, lry = self.bounds
	w, h = self.__name.get_property('layout').get_pixel_size()
	if w > self.width:
	    ulx = (self.width / 2) - (w / 2)
	    lrx = (self.width / 2) + (w / 2)
	self.set_bounds ((ulx, uly, lrx+1, lry + h))

    def on_get_shape_iter(self):
	return self.__head

    def on_shape_next(self, iter):
	if iter is self.__head:
	    return self.__body
	elif iter is self.__body:
	    return self.__arms
	elif iter is self.__arms:
	    return self.__legs
	return None

    def on_shape_value(self, iter):
	return iter

    def on_move(self, x, y):
	self.__name.request_update()
	ModelElementItem.on_move(self, x, y)

    def on_handle_motion (self, handle, wx, wy, mask):
	retval  = ModelElementItem.on_handle_motion(self, handle, wx, wy, mask)
	self.__name_update()
	return retval

    # Groupable

    def on_groupable_add(self, item):
	return 0

    def on_groupable_remove(self, item):
	'''Do not allow the name to be removed.'''
	#self.emit_stop_by_name('remove')
	##return 0
	pass

    def on_groupable_get_iter(self):
	try:
	    return self.__name
	except AttributeError:
	    return None

    def on_groupable_next(self, iter):
	return None

    def on_groupable_value(self, iter):
	return iter

    def on_groupable_length(self):
	return 1

    def on_groupable_pos(self, item):
	if item == self.__name:
	    return 0
	else:
	    return -1

    def on_subject_update(self, name, old_value, new_value):
	if name == 'name':
	    self.__name.set(text=self.subject.name)
	    self.__name_update()
	else:
	    ModelElementItem.on_subject_update(self, name, old_value, new_value)

    def on_text_changed(self, text_item, text):
	if text != self.subject.name:
	    self.subject.name = text
	    self.__name_update()

