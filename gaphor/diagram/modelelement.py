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
	DiagramItem.__init__(self)
	self.subject = None
	self.auto_resize = 0
	self.__id = -1

    def save (self, store):
	store.save_property('affine')
	store.save_property('width')
	store.save_property('height')
	store.save_attribute('subject', self.subject)
	store.save_property('auto-resize')

    def load (self, store):
	for prop in [ 'affine', 'width', 'height', 'auto-resize' ]:
	    self.set_property(prop, eval (store.value(prop)))
	self.set_property('subject', store.reference('subject')[0])

    def postload(self, store):
	pass

    def do_set_property (self, pspec, value):
	if pspec.name == 'id':
	    #print self, 'id', value
	    self.__id = int(value)
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

    def on_connect_handle (self, handle):
	return self._on_connect_handle(handle, diacanvas.CanvasElement)

    def on_disconnect_handle (self, handle):
	return self._on_disconnect_handle(handle, diacanvas.CanvasElement)

    def on_subject_update (self, name, old_value, new_value):
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
