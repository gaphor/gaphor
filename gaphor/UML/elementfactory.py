# vim: sw=4
'''management.py
This module contains some functions for managing UML models. This
includes saving, loading and flushing models. In the future things like
consistency checking should also be included.'''

import modelelements
import diagram
import libxml2 as xml
from misc import Singleton, Signal
#import sys

class ElementFactory(Singleton):

    def __unlink_signal (self, key, obj):
	if (key == '__unlink__' or key == '__hide__') \
		and self.__elements.has_key(obj.id):
	    del self.__elements[obj.id]
	    self.__emit_remove (obj)
	elif key == '__show__' and not self.__elements.has_key(obj.id):
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
	obj.connect (self.__unlink_signal, obj)
	self.__emit_create (obj)
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
	while 1:
	    try:
		(key, value) = self.__elements.popitem()
	    except KeyError:
		break;
	    value.unlink()
	    self.__elements.clear()

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
	for e in self.__elements.values():
	    #print 'Saving object', e
	    e.save(rootnode, ns)

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

	node = rootnode.children
	while node:
	    #if node.name != 'Element' or node.type != 'text':
	    #    raise ValueError, 'No Element tag (%s).' % node.name
	     
	    #print node.__dict__
	    if node.name == 'Element':
		type = node.prop('type')
		#print 'New node: ' + type
		try:
		    if type == 'Diagram':
			cls = getattr (diagram, type)
		    else:
			cls = getattr (modelelements, type)
		except:
		    raise ValueError, 'Could not find class %s.' % type
		# Create the Model element
		id = int (node.prop('id')[1:])
		#print 'node id =', id
		old_index = self.__index
		self.__index = id
		self.create (cls)

		if old_index > id:
		    self.__index = id

		node = node.next
		#if node: print 'Next node:', node.name
	    # Remove text nodes (libxml2 seems to like adding text nodes)
	    elif node.name == 'text':
		next = node.next
		node.unlinkNode ()
		node.freeNode ()
		node = next
		#if node: print 'Next node:', node.name
	    else:
		raise ValueError, 'No Element tag (%s).' % node.name

	# Second step: call Element.load() for every object in the element hash.
	# We also provide the XML node, so it can recreate it's state
	print "Now calling load() for every model element"
	node = rootnode.children
	while node:
	    assert node.name == 'Element'

	    #print 'ID:' + node.prop('id')
	    id = int (node.prop('id')[1:])
	    element = self.lookup (id)
	    print element
	    if not element:
		raise ValueError, 'Element with id %d was created but can not be found anymore.' % id

	    element.load (self, node)
	    
	    node = node.next

	# Do some things after the loading of the objects is done...
	print self.__elements
	#save ('b.xml')
	print "Now calling postload() for every model element"
	node = rootnode.children
	while node:
	    id = int (node.prop('id')[1:])
	    element = self.lookup (id)
	    print element
	    assert element != None
	    element.postload (node)
	    node = node.next

	doc.freeDoc ()

xml.initParser ()
