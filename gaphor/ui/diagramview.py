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


gobject.type_register(DiagramView)
