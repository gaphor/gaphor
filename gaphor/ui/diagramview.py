#!/usr/bin/env python
# vim: sw=4

import gobject
from diacanvas import CanvasView

class DiagramView(CanvasView):

    def __init__(self, canvas):
	self.__gobject_init__()
	CanvasView.__init__(self, canvas)


gobject.type_register(DiagramView)
