'''
PackageItem diagram item
'''
# vim:sw=4

from modelelement import ModelElementItem
import diacanvas
import pango

class PackageItem(ModelElementItem):
    __gsignals__ = { 'need_update': 'override' }
    TAB_X=50
    TAB_Y=20
    MARGIN_X=60
    MARGIN_Y=30
    FONT='sans bold 10'

    def __init__(self):
	ModelElementItem.__init__(self)
	self.set(height=50, width=100)
	self.__border = diacanvas.shape.Path()
	self.__border.set_line_width(2.0)
	self.__name = diacanvas.CanvasText()
	self.add_construction(self.__name)
	assert self.__name != None
	font = pango.FontDescription(PackageItem.FONT)
	self.__name.set(font=font, width=self.width,
			alignment=pango.ALIGN_CENTER)
	# Center the text:
	w, h = self.__name.get_property('layout').get_pixel_size()
	self.__name.move(0, (self.height - h + PackageItem.TAB_Y) / 2)
	self.__name.set(height=h)
	# Hack since self.<method> is not GC'ed
	def on_text_changed(text_item, text, package):
	    if text != package.subject.name:
		package.subject.name = text
		package.__name_update()
	self.__name.connect('text_changed', on_text_changed, self)
	#self.__name.connect('text_changed', self.on_text_changed)

    def __name_update (self):
	'''Center the name text in the package body.'''
	w, h = self.__name.get_property('layout').get_pixel_size()
	self.set(min_width=w + PackageItem.MARGIN_X,
		 min_height=h + PackageItem.MARGIN_Y)
	a = self.__name.get_property('affine')
	aa = (a[0], a[1], a[2], a[3], a[4], \
		(self.height - h + PackageItem.TAB_Y) / 2)
	self.__name.set(affine=aa, width=self.width, height=h)

    def load(self, store):
	ModelElementItem.load(self, store)
	self.__name_update()

    def do_need_update(self):
	'''Always request updates for the aggregated items.'''
	self.__name.request_update()

    def on_update(self, affine):
	ModelElementItem.on_update(self, affine)
	O = 0.0
	H = self.height
	W = self.width
	X = PackageItem.TAB_X
	Y = PackageItem.TAB_Y
	line = ((X, Y), (X, O), (O, O), (O, H), (W, H), (W, Y), (O, Y))
	self.__border.line(line)
	self.__border.request_update()
	self.update_child(self.__name, affine)
	b1, b2, b3, b4 = self.bounds
	self.set_bounds((b1 - 1, b2 - 1, b3 + 1, b4 + 1))

    def on_handle_motion (self, handle, wx, wy, mask):
	retval = ModelElementItem.on_handle_motion(self, handle, wx, wy, mask)
	self.__name_update()
	return retval

    def on_get_shape_iter(self):
	return self.__border

    def on_shape_next(self, iter):
	return None

    def on_shape_value(self, iter):
	return iter

    # Groupable

    def on_groupable_add(self, item):
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

    def on_subject_update(self, name, old_value, new_value):
	if name == 'name':
	    self.__name.set(text=self.subject.name)
	    self.__name_update()
	else:
	    ModelElementItem.on_subject_update(self, name, old_value, new_value)

    def on_text_changed(self, text_item, text):
	if text != self.subject.name:
	    self.subject.name = text

