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
	'id':		(gobject.TYPE_PYOBJECT, 'id',
			 'Identification number of the canvas item',
			 gobject.PARAM_READWRITE),
	'subject':	(gobject.TYPE_PYOBJECT, 'subject',
			 'subject held by the model element',
			 gobject.PARAM_READWRITE),
	'auto-resize':	(gobject.TYPE_BOOLEAN, 'auto resize',
			 'Set auto-resize for the diagram item',
			 1, gobject.PARAM_READWRITE),
    }

    def __init__(self):
	self.__gobject_init__()
	#diacanvas.CanvasElement.__init__(self)
	DiagramItem.__init__(self)
	self.auto_resize = 0
	self.__id = -1

    def set_id(self, value):
	self.__id = value

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
	    self.set_property(name, value)
	else:
	    #log.debug('Setting unknown property "%s" -> "%s"' % (name, value))
	    self.set_property(name, eval(value))

    def postload(self):
	pass

    def do_set_property(self, pspec, value):
	if pspec.name == 'id':
	    self.__id = value
	elif pspec.name == 'subject':
	    #print 'Setting subject:', value
	    self._set_subject(value)
	elif pspec.name == 'auto-resize':
	    self.auto_resize = value
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    def do_get_property(self, pspec):
	if pspec.name == 'id':
	    return self.__id
	elif pspec.name == 'subject':
	    return self.subject
	elif pspec.name == 'auto-resize':
	    return self.auto_resize
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    # DiaCanvasItem callbacks
    def on_glue(self, handle, wx, wy):
	return self._on_glue(handle, wx, wy, diacanvas.CanvasElement)

    def on_connect_handle(self, handle):
	return self._on_connect_handle(handle, diacanvas.CanvasElement)

    def on_disconnect_handle(self, handle):
	return self._on_disconnect_handle(handle, diacanvas.CanvasElement)

    def on_subject_update(self, name, old_value, new_value):
	if name == '__unlink__':
	    #self.set_property('subject', None)
	    if self.parent:
		    self.parent.remove(self)
	else:
	    DiagramItem.on_subject_update(self, name, old_value, new_value)

gobject.type_register(ModelElementItem)
diacanvas.set_callbacks(ModelElementItem)
diacanvas.set_groupable(ModelElementItem)

if __name__ == '__main__':
    me = ModelElementItem()
    print me, me.__gtype__
