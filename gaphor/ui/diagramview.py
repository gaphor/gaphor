#!/usr/bin/env python
# vim: sw=4

import gobject
from diacanvas import CanvasView

class DiagramView(CanvasView):

    def __init__(self, diagram=None):
	self.__gobject_init__()
	if diagram:
	    canvas = diagram.canvas
	else:
	    canvas = None
	CanvasView.__init__(self, canvas)
	self.diagram = diagram
	
    def create(self, type):
	return self.diagram.create(type)

    def set_diagram(self, diagram):
	self.set_canvas (diagram.canvas)
	self.diagram = diagram

    def get_diagram(self):
	return self.diagram

gobject.type_register(DiagramView)
