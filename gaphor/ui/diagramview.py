#!/usr/bin/env python
# vim: sw=4

import gobject
import gtk
from diacanvas import CanvasView

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
	self.diagram = diagram
	# Drop
	self.drag_dest_set (gtk.DEST_DEFAULT_ALL, DiagramView.DND_TARGETS,
			    gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_LINK)
	self.connect('drag_data_received', DiagramView.do_drag_data_received)
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
   
    def do_drag_data_received(self, context, x, y, data, info, time):
	print 'drag_data_received'
        if data and data.format == 8 and info == DiagramView.TARGET_ELEMENT_ID:
	    import gaphor.UML as UML
	    import gaphor.diagram as diagram
	    print 'drag_data_received:', data.data, info
	    elemfact = GaphorResource('ElementFactory')
	    element = elemfact.lookup(int(data.data))
	    assert element
	    if isinstance(element, UML.Actor):
		item = self.create (diagram.ActorItem)
	    elif isinstance(element, UML.UseCase):
		item = self.create (diagram.UseCaseItem)
	    else:
		item = None
	    # Move the item:
	    if item:
		wx, wy = self.window_to_world(x + self.get_hadjustment().value,
					      y + self.get_vadjustment().value)
		ix, iy = item.affine_point_w2i(wx, wy)
		item.move(ix, iy)
		item.set_property ('subject', element)
		print 'item.subject;', item.subject
	    context.finish(gtk.TRUE, gtk.FALSE, time)
	else:
	    context.finish(gtk.FALSE, gtk.FALSE, time)

    def do_drag_drop(self, context, x, y, time):
	print 'drag_drop'
	return 1

gobject.type_register(DiagramView)
