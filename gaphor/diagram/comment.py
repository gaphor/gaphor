'''
CommentItem diagram item
'''
# vim:sw=4

from UML import Comment
import registrar
from modelelement import ModelElementItem
import diacanvas
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
	self.add(diacanvas.CanvasText())
	assert self.__name != None
	font = pango.FontDescription(CommentItem.FONT)
	self.__name.set(font=font, width=self.width - (CommentItem.OFFSET * 2),
			alignment=pango.ALIGN_LEFT)
	w, h = self.__name.get_property('layout').get_pixel_size()
	#print 'CommentItem:',w,h
	self.__name.move(CommentItem.OFFSET, CommentItem.OFFSET)
	self.__name_update()
	#self.__name.set(height=h, width=self.width)
	self.__name.connect_object('text_changed', CommentItem.on_text_changed, self)

    def __name_update (self):
	'''Center the name text in the usecase.'''
	w, h = self.__name.get_property('layout').get_pixel_size()
	self.set(min_height=h + CommentItem.OFFSET * 2)
	#a = self.__name.get_property('affine')
	#aa = (a[0], a[1], a[2], a[3], a[4], (self.height - h) / 2)
	#self.__name.set(affine=aa, width=self.width, height=h)
	self.__name.set(width=self.width - CommentItem.EAR - CommentItem.OFFSET,
			height=self.height - CommentItem.OFFSET * 2)
	print 'Comment:', w, h, self.width, self.height

    def load(self, store):
	ModelElementItem.load(self, store)
	self.__name_update()

    def on_update(self, affine):
	ModelElementItem.on_update(self, affine)
	# Width and height, adjusted for line width...
	w = self.width - 1
	h = self.height - 1
	ear = CommentItem.EAR
	self.__border.line(((w - ear, 1), (w- ear, ear), (w, ear), (w - ear, 1),
			    (1, 1), (1, h), (w, h), (w, ear)))
	self.__border.request_update()
	self.__name.update_now()

    def on_get_shape_iter(self):
	return self.__border

    def on_shape_next(self, iter):
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
	try:
	    if self.__name is not None:
		raise AttributeError, 'No more canvas items should be set'
	except AttributeError:
	    self.__name = item
	    return 1
	return 0

    def on_groupable_remove(self, item):
	'''Do not allow the name to be removed.'''
	self.emit_stop_by_name('remove')
	return 0

    def on_groupable_get_iter(self):
	return self.__name

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

    def on_subject_update(self, name):
	if name == 'name':
	    self.__name.set(text=self.subject.name)
	    self.__name_update()
	else:
	    ModelElementItem.on_subject_update(self, name)

    def on_text_changed(self, text):
	self.__name_update()
	if text != self.subject.name:
	    self.subject.name = text

registrar.register(CommentItem, Comment)
