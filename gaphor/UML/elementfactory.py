# vim: sw=4
'''elementfactory.py
'''

#import misc.singleton as Singleton
from gaphor.misc.signal import Signal as _Signal
import gaphor.misc.uniqueid as uniqueid
import weakref, gc
from element import Element
from modelelements import Model
from diagram import Diagram

class ElementFactory(object):
    '''The ElementFactory is used to create elements ans do lookups to
    elements. A model can contain only one Model element, though.
    '''
    def __element_signal (self, key, old_value, new_value, obj):
	element = obj()
	if not element:
	    return
	if key == '__unlink__' and self.__elements.has_key(element.id):
	    log.debug('Unlinking element: %s' % element)
	    del self.__elements[element.id]
	    self.__emit_remove (element)
	    if isinstance (element, Model):
		self.__model = None
	elif key == '__relink__' and not self.__elements.has_key(element.id):
	    log.debug('Relinking element: %s' % element)
	    self.__elements[element.id] = element
	    if isinstance (element, Model):
		self.__model = element
	    self.__emit_create (element)

    def __init__ (self):
	self.__elements = { }
	self.__signal = _Signal()
	self.__model = None

    def create (self, type):
	'''Create a new Model element of type type'''
	return self.create_as(type, uniqueid.generate_id())

    def create_as (self, type, id):
	'''Create a new model element of type 'type' with 'id' as its ID.
	This method should only be used when loading models. If the ID is
	higher that the current id that should be used for the next item, the
	ID for the next item is set to id + 1.'''
	assert issubclass(type, Element)
	if type is Model and self.__model:
	    raise ValueError, 'Trying to create a Model element, while there already is a model'
        obj = type(id)
	self.__elements[id] = obj
	obj.connect (self.__element_signal, weakref.ref(obj))
	if type is Model:
	    self.__model = obj
	self.__emit_create (obj)
	return obj

    def lookup (self, id):
	try:
	    return self.__elements[id]
	except KeyError:
	    return None

    def get_model(self):
	return self.__model

    def select(self, expression):
	l = []
	for e in self.__elements.values():
	    if expression(e):
		l.append(e)
	return l

    def keys (self):
        return self.__elements.keys()

    def values (self):
        return self.__elements.values()

    def flush(self):
	'''Flush all elements in the UML.elements table.'''
	#for key, value in self.__elements.items():
	#    value._Element__flush()

	for key, value in self.__elements.items():
	    #print 'ElementFactory: unlinking', value
	    #print 'references:', gc.get_referrers(value)
	    if isinstance (value, Diagram):
		value.canvas.clear_undo()
		value.canvas.clear_redo()
	    value.unlink()
	assert len(self.__elements) == 0, 'Still items in the factory: %s' % str(self.__elements.values())
	#self.__index = 1

    def connect (self, signal_func, *data):
	self.__signal.connect (signal_func, *data)

    def disconnect (self, signal_func):
	self.__signal.disconnect (signal_func)

    def __emit_create (self, obj):
	self.__signal.emit ('create', obj)

    def __emit_remove (self, obj):
	self.__signal.emit ('remove', obj)

    def __element_destroyed(self, obj):
	#print 'ElementFactory::element_destroyed...'
	obj().disconnect_by_data(obj)


GaphorResource(ElementFactory)
