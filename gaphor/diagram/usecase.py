'''
UseCase diagram item
'''
# vim:sw=4

import UML
import gobject
from modelelement import ModelElement
import diacanvas

class UseCase(ModelElement):

    def __init__(self):
	ModelElement.__init__(self)
	self.border = diacanvas.shape.Ellipse()
	self.border.set_line_width(0.4)
	self.border.ellipse(center=(self.width / 2, self.height / 2), \
			    width=self.width, height=self.height)

    def on_update(self, affine):
	ModelElement.on_update(self, affine)
	self.border.ellipse(center=(self.width / 2, self.height / 2), \
			    width=self.width, height=self.height)
	self.border.request_update()

    def on_get_shape_iter(self):
	return self.border

    def on_shape_next(self, iter):
	return None

    def on_shape_value(self, iter):
	return iter

gobject.type_register (UseCase)

print 'UseCase done'
