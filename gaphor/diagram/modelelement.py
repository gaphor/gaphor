'''
ModelElementItem

Abstract base class for element-like Diagram items.
'''
# vim:sw=4

if __name__ == '__main__':
    import sys
    sys.path.append('..')
    del sys

import gobject
import diacanvas as dia
#from metaitem import MetaItem
#from UML import Element

__revision__ = '$revision$'
__author__ = 'Arjan J. Molenaar'
__date__ = '$date$'


class ModelElementItem (dia.CanvasElement, dia.CanvasAbstractGroup):
#    __metaclass__ = MetaItem
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
	self.subject = None
	self.auto_resize = 0
	self.__id = -1
	self.connect ('notify::parent', ModelElementItem.on_parent_notify)

    def save (self, store):
	store.save_property('affine')
	store.save_property('width')
	store.save_property('height')
	store.save('subject', self.subject)
	store.save_property('auto-resize')

    def load (self, store):
	for prop in [ 'affine', 'width', 'height', 'auto-resize' ]:
	    self.set_property(prop, eval (store.value(prop)))
	self.set_property('subject', store.reference('subject')[0])

    def do_set_property (self, pspec, value):
	if pspec.name == 'id':
	    self.__id = int(value)
	elif pspec.name == 'subject':
	    print 'Setting subject:', value
	    self.preserve_property('subject')
	    if value != self.subject:
		if self.subject:
		    self.subject.remove_presentation(self)
		    self.subject.disconnect(self.on_subject_update)
		self.subject = value
		if value:
		    value.connect(self.on_subject_update)
		    value.add_presentation(self)

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
	return dia.CanvasElement.on_glue (self, handle, wx, wy)

    def on_connect_handle (self, handle):
	return dia.CanvasElement.on_connect_handle (self, handle)

    def on_disconnect_handle (self, handle):
	return dia.CanvasElement.on_disconnect_handle (self, handle)

    def on_parent_notify (self, parent):
	print self
	if self.subject:
	    if self.parent:
		print 'Have Parent', self, parent
		self.subject.add_presentation (self)
	    else:
		print 'No parent...', self, parent
		self.subject.remove_presentation (self)

    def on_subject_update (self, name):
	if name == '__unlink__':
	    #self.set_property('subject', None)
	    if self.parent:
		    self.parent.remove(self)
	else:
	    print 'ModelElementItem: unhandled signal "%s"' % str(name)

gobject.type_register(ModelElementItem)
dia.set_callbacks(ModelElementItem)
dia.set_groupable(ModelElementItem)

if __name__ == '__main__':
    me = ModelElementItem()
    print me, me.__gtype__
