# vim:sw=4
'''
ModelElementItem

Abstract base class for element-like Diagram items.
'''

import gobject
import diacanvas
from diagramitem import DiagramItem

__revision__ = '$revision$'
__author__ = 'Arjan J. Molenaar'
__date__ = '$date$'


class ModelElementItem (diacanvas.CanvasElement, \
			diacanvas.CanvasGroupable, \
			DiagramItem):
    # Properties, also add the DiagramItem properties here.
    __gproperties__ = {
        'auto-resize':        (gobject.TYPE_BOOLEAN, 'auto resize',
                         'Set auto-resize for the diagram item',
                         1, gobject.PARAM_READWRITE)
    }
    __gproperties__.update(DiagramItem.__gproperties__)

    __gsignals__ = DiagramItem.__gsignals__

    def __init__(self, id=None):
        self.__gobject_init__()
        #diacanvas.CanvasElement.__init__(self)
        DiagramItem.__init__(self, id)
        self.auto_resize = 0

    def save(self, save_func):
        for prop in ('affine', 'width', 'height', 'auto-resize'):
            self.save_property(save_func, prop)
        DiagramItem.save(self, save_func)

    def load(self, name, value):
        if name == 'subject':
            self.subject = value
        else:
            #log.debug('Setting unknown property "%s" -> "%s"' % (name, value))
            self.set_property(name, eval(value))

    def do_set_property(self, pspec, value):
        if pspec.name == 'auto-resize':
            self.preserve_property('auto-resize')
            self.auto_resize = value
        else:
            DiagramItem.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
        if pspec.name == 'auto-resize':
            return self.auto_resize
        else:
            return DiagramItem.do_get_property(self, pspec)

    # Ensure we call the right connect functions:
    connect = DiagramItem.connect
    disconnect = DiagramItem.disconnect

    # DiaCanvasItem callbacks
    def on_glue(self, handle, wx, wy):
        return self._on_glue(handle, wx, wy, diacanvas.CanvasElement)

    def on_connect_handle(self, handle):
        return self._on_connect_handle(handle, diacanvas.CanvasElement)

    def on_disconnect_handle(self, handle):
        return self._on_disconnect_handle(handle, diacanvas.CanvasElement)


gobject.type_register(ModelElementItem)
diacanvas.set_callbacks(ModelElementItem)
diacanvas.set_groupable(ModelElementItem)
