'''
CommentItem diagram item
'''
# vim:sw=4

from modelelement import ModelElementItem
import diacanvas
import gobject
import pango

class CommentItem(ModelElementItem):
    EAR=15
    OFFSET=5
    FONT='sans 10'

    def __init__(self):
	ModelElementItem.__init__(self)
	self.set(min_width=CommentItem.EAR + 2 * CommentItem.OFFSET,
		 height=50, width=100)
	self.__border = diacanvas.shape.Path()
	self.__border.set_line_width(2.0)
	self.__body = diacanvas.CanvasText()
	self.add_construction(self.__body)
	assert self.__body != None
	font = pango.FontDescription(CommentItem.FONT)
	self.__body.set(font=font, width=self.width - (CommentItem.OFFSET * 2),
			alignment=pango.ALIGN_LEFT)
	w, h = self.__body.get_property('layout').get_pixel_size()
	#print 'CommentItem:',w,h
	self.__body.move(CommentItem.OFFSET, CommentItem.OFFSET)
	self.__body_update()
	#self.__body.set(height=h, width=self.width)
	# Hack since self.<method> is not GC'ed
	def on_text_changed(text_item, text, actor):
	    if text != actor.subject.body:
		actor.subject.body = text
		actor.__body_update()
	self.__body.connect('text_changed', on_text_changed, self)
	#self.__body.connect('text_changed', self.on_text_changed)

    def __body_update (self):
	'''Center the body text in the usecase.'''
	w, h = self.__body.get_property('layout').get_pixel_size()
	self.set(min_height=h + CommentItem.OFFSET * 2)
	#a = self.__body.get_property('affine')
	#aa = (a[0], a[1], a[2], a[3], a[4], (self.height - h) / 2)
	#self.__body.set(affine=aa, width=self.width, height=h)
	self.__body.set(width=self.width - CommentItem.EAR - CommentItem.OFFSET,
			height=self.height - CommentItem.OFFSET * 2)
	#print 'Comment:', w, h, self.width, self.height

    def load(self, store):
	ModelElementItem.load(self, store)
	self.__body_update()

    def on_update(self, affine):
	ModelElementItem.on_update(self, affine)
	# Width and height, adjusted for line width...
	w = self.width
	h = self.height
	ear = CommentItem.EAR
	self.__border.line(((w - ear, 0), (w- ear, ear), (w, ear), (w - ear, 0),
			    (0, 0), (0, h), (w, h), (w, ear)))
	self.__border.request_update()
	self.expand_bounds(1)
	self.update_child(self.__body, affine)

    def on_get_shape_iter(self):
	return self.__border

    def on_shape_next(self, iter):
	return None

    def on_shape_value(self, iter):
	return iter

    def on_move(self, x, y):
	self.__body.request_update()
	ModelElementItem.on_move(self, x, y)

    def on_handle_motion (self, handle, wx, wy, mask):
	retval  = ModelElementItem.on_handle_motion(self, handle, wx, wy, mask)
	self.__body_update()
	return retval

    def on_event (self, event):
	if event.type == diacanvas.EVENT_KEY_PRESS:
	    self.__body.focus()
	    self.__body.on_event (event)
	    return True
	else:
	    return ModelElementItem.on_event(self, event)

    # Groupable

    def on_groupable_add(self, item):
	return 0

    def on_groupable_remove(self, item):
	'''Do not allow the body to be removed.'''
	self.emit_stop_by_name('remove')
	return 0

    def on_groupable_get_iter(self):
	return self.__body

    def on_groupable_next(self, iter):
	return None

    def on_groupable_value(self, iter):
	return iter

    def on_groupable_length(self):
	return 1

    def on_groupable_pos(self, item):
	if item == self.__body:
	    return 0
	else:
	    return -1

    def on_subject_update(self, name, old_value, new_value):
	if name == 'body':
	    self.__body.set(text=self.subject.body)
	    self.__body_update()
	else:
	    ModelElementItem.on_subject_update(self, name, old_value, new_value)

    def on_text_changed(self, text_item, text):
	self.__body_update()
	if text != self.subject.body:
	    self.subject.body = text

gobject.type_register(CommentItem)

