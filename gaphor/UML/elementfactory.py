# vim: sw=4
'''management.py
This module contains some functions for managing UML models. This
includes saving, loading and flushing models. In the future things like
consistency checking should also be included.'''

#import misc.singleton as Singleton
from gaphor.misc.signal import Signal as _Signal
#from misc.storage import Storage
import weakref, gc
from element import Element
from diagram import Diagram

class ElementFactory(object):

    def __element_signal (self, key, old_value, new_value, obj):
	element = obj()
	if not element:
	    return
	if key == '__unlink__' and self.__elements.has_key(element.id):
	    print 'Unlinking element', element
	    del self.__elements[element.id]
	    self.__emit_remove (element)
	elif key == '__relink__' and not self.__elements.has_key(element.id):
	    print 'Relinking element', element
	    self.__elements[element.id] = element
	    self.__emit_create (element)

    def __init__ (self):
	self.__elements = { }
	self.__index = 1
	self.__signal = _Signal()

    def create (self, type):
        obj = type(self.__index)
	self.__elements[self.__index] = obj
	self.__index += 1
	obj.connect (self.__element_signal, weakref.ref(obj))
	self.__emit_create (obj)
	#print 'ElementFactory:', str(self.__index), 'elements in the factory'
	return obj

    def create_as (self, type, id):
	'''Create a new model element of type 'type' with 'id' as its ID.
	This method should only be used when loading models. If the ID is
	higher that the current id that should be used for the next item, the
	ID for the next item is set to id + 1.'''
	old_index = self.__index
	self.__index = id
	self.create (type)
	if old_index > self.__index:
	    self.__index = old_index

    def lookup (self, id):
	try:
	    return self.__elements[id]
	except KeyError:
	    return None

    def keys (self):
        return self.__elements.keys()

    def values (self):
        return self.__elements.values()

    def flush(self):
	'''Flush all elements in the UML.elements table.'''
	#for key, value in self.__elements.items():
	#    value._Element__flush()

	for key, value in self.__elements.items():
	    print 'ElementFactory: unlinking', value
	    #print 'references:', gc.get_referrers(value)
	    if isinstance (value, Diagram):
		value.canvas.clear_undo()
		value.canvas.clear_redo()
	    value.unlink()
	assert len(self.__elements) == 0, 'Still items in the factory: %s' % str(self.__elements.values())
	self.__index = 1

    def connect (self, signal_func, *data):
	self.__signal.connect (signal_func, *data)

    def disconnect (self, signal_func):
	self.__signal.disconnect (signal_func)

    def __emit_create (self, obj):
	self.__signal.emit ('create', obj)

    def __emit_remove (self, obj):
	self.__signal.emit ('remove', obj)

    def __element_destroyed(self, obj):
	print 'ElementFactory::element_destroyed...'
	obj().disconnect_by_data(obj)

    def values(self):
	return self.__elements.values()

GaphorResource(ElementFactory)
