#!/usr/bin/env python
# vim: sw=4

import gobject
import gtk
from diacanvas import CanvasView

class DiagramView(CanvasView):
    TARGET_STRING = 0
    DND_TARGETS = [
	('STRING', 0, TARGET_STRING),
	('text/plain', 0, TARGET_STRING)]
    __gsignals__ = { 'drag_data_received': 'override',
		     'drag_motion': 'override',
		     'drag_drop': 'override' }

    def __init__(self, diagram=None):
	from namespace import NamespaceView
	self.__gobject_init__()
	self.drag_dest_set (gtk.DEST_DEFAULT_DROP, DiagramView.DND_TARGETS,
			    gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_LINK)
	#self.connect('drag_data_received', DiagramView.do_drag_data_received)
	#self.connect('drag_motion', DiagramView.do_drag_motion)
	#self.connect('drag_drop', DiagramView.do_drag_drop)
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

    def do_drag_motion(self, context, x, y, time):
	print 'drag_motion', x, y
	return 1
   
    def do_drag_data_received(self, w, context, x, y, data, info, time):
	print 'drag_data_received'
        if data and data.format == 8:
	    print 'drag_data_received:', data.data
	    context.finish(gtk.TRUE, gtk.FALSE, time)
	else:
	    context.finish(gtk.FALSE, gtk.FALSE, time)

    def do_drag_drop(self, context, x, y, time):
	print 'drag_drop'
	return 1

gobject.type_register(DiagramView)
