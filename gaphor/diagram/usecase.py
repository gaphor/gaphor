'''
eseCaseItempango diagram item
'''
# vim:sw=4

import gobject
import pango
import diacanvas

from classifier import ClassifierItem

class UseCaseItem(ClassifierItem):
    MARGIN_X=60
    MARGIN_Y=30

    def __init__(self, id=None):
	ClassifierItem.__init__(self, id)
	self.set(height=50, width=100)
	self._border = diacanvas.shape.Ellipse()
	self._border.set_line_width(2.0)

    # DiaCanvasItem callbacks:

    def on_update(self, affine):
	# Center the text
	layout = self._name.get_property('layout')
	#layout.set_width(-1)
	w, h = layout.get_pixel_size()
	self.set(min_width=w + UseCaseItem.MARGIN_X,
		 min_height=h + UseCaseItem.MARGIN_Y)
	a = self._name.get_property('affine')
	aa = (a[0], a[1], a[2], a[3], 0.0, (self.height - h) / 2)
	self._name.set(affine=aa, width=self.width, height=h)

	ClassifierItem.on_update(self, affine)

	self._border.ellipse(center=(self.width / 2, self.height / 2),
			      width=self.width, height=self.height)
	self.expand_bounds(1.0)

    def on_shape_iter(self):
	return iter([self._border])


gobject.type_register(UseCaseItem)
