'''
CommentItem diagram item
'''
# vim:sw=4

from modelelement import ModelElementItem
import diacanvas
import pango

class CommentItem(ModelElementItem):
    __gsignals__ = { 'need_update': 'override' }
    EAR=15
    OFFSET=5
    FONT='sans 10'

    def __init__(self):
	ModelElementItem.__init__(self)
	self.set(min_width=CommentItem.EAR + 2 * CommentItem.OFFSET,
		 height=50, width=100)
	self.__border = diacanvas.shape.Path()
	self.__border.set_line_width(2.0)
	self.add(diacanvas.CanvasText())
	assert self.__body != None
	font = pango.FontDescription(CommentItem.FONT)
	self.__body.set(font=font, width=self.width - (CommentItem.OFFSET * 2),
			alignment=pango.ALIGN_LEFT)
	w, h = self.__body.get_property('layout').get_pixel_size()
	#print 'CommentItem:',w,h
	self.__body.move(CommentItem.OFFSET, CommentItem.OFFSET)
	self.__body_update()
	#self.__body.set(height=h, width=self.width)
	self.__body.connect_object('text_changed', CommentItem.on_text_changed, self)

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

    def do_need_update(self):
	self.__body.request_update()

    def on_update(self, affine):
	ModelElementItem.on_update(self, affine)
	# Width and height, adjusted for line width...
	w = self.width - 1
	h = self.height - 1
	ear = CommentItem.EAR
	self.__border.line(((w - ear, 1), (w- ear, ear), (w, ear), (w - ear, 1),
			    (1, 1), (1, h), (w, h), (w, ear)))
	self.__border.request_update()
	self.update_child(affine, self.__body)

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

    # Groupable

    def on_groupable_add(self, item):
	try:
	    if self.__body is not None:
		raise AttributeError, 'No more canvas items should be set'
	except AttributeError:
	    self.__body = item
	    return 1
	return 0

    def on_groupable_remove(self, item):
	'''Do not allow the body to be removed.'''
	self.emit_stop_by_body('remove')
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

    def on_text_changed(self, text):
	self.__body_update()
	if text != self.subject.body:
	    self.subject.body = text

