# vim: sw=4
'''management.py
This module contains some functions for managing UML models. This
includes saving, loading and flushing models. In the future things like
consistency checking should also be included.'''

import misc.singleton as Singleton
import misc.signal as Signal
import misc.storage as Storage
import libxml2 as xml
from element import Element

class ElementFactory(Singleton):
    NS = None

    def __element_signal (self, key, obj):
	if key == '__unlink__' and self.__elements.has_key(obj.id):
	    print 'Unlinking element', obj
	    del self.__elements[obj.id]
	    self.__emit_remove (obj)
	elif key == '__relink__' and not self.__elements.has_key(obj.id):
	    print 'Relinking element', obj
	    self.__elements[obj.id] = obj
	    self.__emit_create (obj)

    def init (self, *args, **kwargs):
	self.__elements = { }
	self.__index = 1
	self.__signal = Signal()

    def create (self, type):
        obj = type(self.__index)
	self.__elements[self.__index] = obj
	self.__index += 1
	obj.connect (self.__element_signal, obj)
	self.__emit_create (obj)
	print 'ElementFactory:', str(self.__index), 'elements in the factory'
	return obj

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
	for key, value in self.__elements.items():
	    value.unlink()
	assert len(self.__elements) == 0
	return None
	while 1:
	    try:
		(key, value) = self.__elements.popitem()
	    except KeyError:
		break;
	    value.unlink()
	    assert len(self.__elements) == 0

    def connect (self, signal_func, *data):
	self.__signal.connect (signal_func, *data)

    def disconnect (self, signal_func):
	self.__signal.disconnect (signal_func)

    def __emit_create (self, obj):
	self.__signal.emit ('create', obj)

    def __emit_remove (self, obj):
	self.__signal.emit ('remove', obj)

    def save (self, filename=None):
	'''Save the current model to @filename. If no filename is given,
	standard out is used.'''
	doc = xml.newDoc ('1.0')
	ns = None
	rootnode = doc.newChild (ns, 'Gaphor', None)
	rootnode.setProp ('version', '1.0')
	store = Storage(self, ElementFactory.NS, rootnode)
	for e in self.__elements.values():
	    #print 'Saving object', e
	    e.save(store.new(e))

	if not filename:
	    filename = '-'

	#doc.saveFormatFile (filename, 2)
	doc.saveFormatFileEnc (filename, 'UTF-8', 1)
	doc.freeDoc ()

    def load (self, filename):
	'''Load a file and create a model if possible.
	Exceptions: IOError, ValueError.'''

	doc = xml.parseFile (filename)
	#doc.debugDumpDocument (sys.stdout)
	# Now iterate over the tree and create every element in the
	# self.elements table.
	rootnode = doc.children
	if rootnode.name != 'Gaphor':
	    raise ValueError, 'File %s is not a Gaphor file.' % filename

	# Set store to the first child element of rootnode.
	first_store = Storage(self, ElementFactory.NS, rootnode)
	print 'first_store =', first_store.__dict__
	first_store = first_store.child()
	# Create plain elements in the factory
	print 'first_store =', first_store.__dict__
	store = first_store
	while store:
	    print 'Creating object of type', store.type()
	    type = store.type()
	    if not issubclass(type, Element):
		raise ValueError, 'Not an UML.Element'

	    id = store.id()
	    old_index = self.__index
	    self.__index = id
	    self.create (type)

	    if old_index > id:
		self.__index = id

	    store = store.next()

	# Second step: call Element.load() for every object in the element hash.
	# We also provide the XML node, so it can recreate it's state
	print "Now calling load() for every model element"
	store = first_store
	while store:
	    element = self.lookup (store.id())
	    print element
	    if not element:
		raise ValueError, 'Element with id %d was created but can not be found anymore.' % id

	    element.load (store)
	    
	    store = store.next()

	# Do some things after the loading of the objects is done...
	print self.__elements
	#save ('b.xml')
	print "Now calling postload() for every model element"
	store = first_store
	while store:
	    element = self.lookup (store.id())
	    print element
	    if not element:
		raise ValueError, 'Element with id %d was created but can not be found anymore.' % id

	    element.postload (store)
	    
	    store = store.next()

	doc.freeDoc ()

