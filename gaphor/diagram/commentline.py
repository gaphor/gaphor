'''
CommentLine -- A line that connects a comment to another model element.
'''
# vim:sw=4

import gobject
import diacanvas

class CommentLineItem(diacanvas.CanvasLine):
    __gproperties__ = {
	'id':		(gobject.TYPE_PYOBJECT, 'id',
			 'Identification number of the canvas item',
			 gobject.PARAM_READWRITE),
    }
    def __init__(self):
	self.__gobject_init__()
	self.__id = -1
	self.set_property('dash', (10.0, 10.0))

    def save (self, store):
	pass

    def load (self, store):
	pass

    def do_set_property (self, pspec, value):
	if pspec.name == 'id':
	    print self, 'id', value
	    self.__id = int(value)
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    def do_get_property(self, pspec):
	if pspec.name == 'id':
	    return self.__id
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

gobject.type_register(CommentLineItem)
diacanvas.set_callbacks(CommentLineItem)
