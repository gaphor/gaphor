#!/usr/bin/env python
# vim: sw=4

import gobject
import gtk
from diacanvas import CanvasView
import gaphor
from gaphor.diagram import get_diagram_item
from gaphor.diagram.itemtool import ItemTool

class DiagramView(CanvasView):
    TARGET_STRING = 0
    TARGET_ELEMENT_ID = 1
    DND_TARGETS = [
	('gaphor/element-id', 0, TARGET_ELEMENT_ID)]
#    __gsignals__ = { 'drag_data_received': 'override',
#		     'drag_motion': 'override',
#		     'drag_drop': 'override' }

    def __init__(self, diagram=None):
	self.__gobject_init__()

	if diagram:
	    canvas = diagram.canvas
	else:
	    canvas = None
	CanvasView.__init__(self, canvas)
	item_tool = ItemTool()
	self.get_default_tool().set_item_tool(item_tool)
	self.diagram = diagram
	# Drop
	self.drag_dest_set (gtk.DEST_DEFAULT_ALL, DiagramView.DND_TARGETS,
			    gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_LINK)
	self.connect('drag_data_received', DiagramView.on_drag_data_received)
	#self.connect('drag_motion', DiagramView.do_drag_motion)
	#self.connect('drag_drop', DiagramView.do_drag_drop)
	
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
   
    def on_drag_data_received(self, context, x, y, data, info, time):
	#rint 'drag_data_received'
        if data and data.format == 8 and info == DiagramView.TARGET_ELEMENT_ID:
	    #print 'drag_data_received:', data.data, info
	    elemfact = gaphor.resource('ElementFactory')
	    element = elemfact.lookup(data.data)
	    assert element
	    item_class = get_diagram_item(element.__class__)
	    if item_class:
		item = self.create(item_class)
		assert item
		wx, wy = self.window_to_world(x + self.get_hadjustment().value,
					      y + self.get_vadjustment().value)
		ix, iy = item.affine_point_w2i(max(0, wx), max(0, wy))
		item.move(ix, iy)
		item.set_property ('subject', element)
	    else:
		log.warning ('No graphical representation for UML element %s', element.__class__.__name__)
	    context.finish(gtk.TRUE, gtk.FALSE, time)
	else:
	    context.finish(gtk.FALSE, gtk.FALSE, time)

    def do_drag_drop(self, context, x, y, time):
	#print 'drag_drop'
	return 1

gobject.type_register(DiagramView)
