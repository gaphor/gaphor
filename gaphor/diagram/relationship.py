'''
Relationship -- Base class for dependencies and associations.
'''
# vim:sw=4

import gobject
import diacanvas
import gaphor.UML as UML
from gaphor.diagram import initialize_item
from diagramitem import DiagramItem
from diagramline import DiagramLine

class RelationshipItem(DiagramLine, DiagramItem):
    __gproperties__ = DiagramItem.__gproperties__

    __gsignals__ = DiagramItem.__gsignals__
    
    def __init__(self, id=None):
        DiagramLine.__init__(self)
        DiagramItem.__init__(self, id)

    def save (self, save_func):
        DiagramItem.save(self, save_func)
        DiagramLine.save(self, save_func)

    def load (self, name, value):
        if name == 'subject':
	    DiagramItem.load(self, name, value)
        else:
	    DiagramLine.load(self, name, value)

    def postload(self):
        DiagramItem.postload(self)
        DiagramLine.postload(self)

#    def do_set_property (self, pspec, value):
#        DiagramItem.do_set_property(self, pspec, value)

#    def do_get_property(self, pspec):
#       return DiagramItem.do_get_property(self, pspec)

    # Ensure we call the right connect functions:
    connect = DiagramItem.connect
    disconnect = DiagramItem.disconnect

    def has_capability(self, capability):
        return super(RelationshipItem, self).has_capability(capability)

    # DiaCanvasItem callbacks
    def on_glue(self, handle, wx, wy):
        return self._on_glue(handle, wx, wy, diacanvas.CanvasLine)

    def on_connect_handle (self, handle):
        return self._on_connect_handle(handle, diacanvas.CanvasLine)

    def on_disconnect_handle (self, handle):
        return self._on_disconnect_handle(handle, diacanvas.CanvasLine)


initialize_item(RelationshipItem)
