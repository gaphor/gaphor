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


class ModelElementItem (diacanvas.CanvasElement, diacanvas.CanvasAbstractGroup, DiagramItem):
    __gproperties__ = {
	'subject':	(gobject.TYPE_PYOBJECT, 'subject',
			 'subject held by the model element',
			 gobject.PARAM_READWRITE),
	'auto-resize':	(gobject.TYPE_BOOLEAN, 'auto resize',
			 'Set auto-resize for the diagram item',
			 1, gobject.PARAM_READWRITE),
    }

    __gsignals__ = { '__unlink__': DiagramItem.signal_prototype,
		     '__relink__': DiagramItem.signal_prototype
    }

    def __init__(self, id=None):
	self.__gobject_init__()
	#diacanvas.CanvasElement.__init__(self)
	DiagramItem.__init__(self, id)
	self.auto_resize = 0
	self._subject = None

    def save(self, save_func):
	self.save_property(save_func, 'affine')
	self.save_property(save_func, 'width')
	self.save_property(save_func, 'height')
	save_func('subject', self.subject)
	self.save_property(save_func, 'auto-resize')

    def load(self, name, value):
	#if name in ( 'affine', 'width', 'height', 'auto-resize' ):
	#if name == 'subject':
	#self.set_property('subject', store.reference('subject')[0])
	if name == 'subject':
	    self._subject = value
	else:
	    #log.debug('Setting unknown property "%s" -> "%s"' % (name, value))
	    self.set_property(name, eval(value))

    def postload(self):
	pass

    def do_set_property(self, pspec, value):
	if pspec.name == 'subject':
	    #print 'Setting subject:', value
	    # property is preserved by self.subject's property
	    if value is not self._subject:
		self.preserve_property('subject')
		if self._subject:
		    self._subject.disconnect('__unlink__', self.__on_unlink, obj, value)
		s = self._subject
		self._subject = value
		if len(s.presentation) == 0:
		    s.unlink()
		if value:
		    value.connect('__unlink__', self.__on_unlink, obj, value)
	elif pspec.name == 'auto-resize':
	    self.preserve_property('auto-resize')
	    self.auto_resize = value
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    def do_get_property(self, pspec):
	if pspec.name == 'subject':
	    return self._subject
	elif pspec.name == 'auto-resize':
	    return self.auto_resize
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

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
