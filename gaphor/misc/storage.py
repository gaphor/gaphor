# vim: sw=4

import UML
import diagram
import diacanvas
import types
import libxml2 as xml


class Storage(object):
    NS=None
    ELEMENT='Element'
    CANVAS='Canvas'
    CANVAS_ITEM='CanvasItem'
    VALUE='Value'
    REFERENCE='Reference'
    NAME='name'
    TYPE='type'
    ID='id'
    CID='cid'
    REFID='refid'
    PVALUE='value'

    def __init__(self, factory, node=None, obj=None):
	object.__init__(self)
	self.__factory = factory
	self.__node = node
	self.__obj = obj

    def save (self, filename=None):
	'''Save the current model to @filename. If no filename is given,
	standard out is used.'''
	doc = xml.newDoc ('1.0')
	rootnode = doc.newChild (Storage.NS, 'Gaphor', None)
	rootnode.setProp ('version', '1.0')
	store = Storage(self.__factory, rootnode)
	for e in self.__factory.values():
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
	first_store = Storage(self.__factory, rootnode)
	#print 'first_store =', first_store.__dict__
	first_store = first_store.child()
	# Create plain elements in the factory
	#print 'first_store =', first_store.__dict__
	store = first_store
	while store:
	    #print 'Creating object of type', store.type()
	    type = store.type()
	    if not issubclass(type, UML.Element):
		raise ValueError, 'Not an UML.Element'

	    self.__factory.create_as (type, store.id())

	    store = store.next()

	# Second step: call Element.load() for every object in the element hash.
	# We also provide the XML node, so it can recreate it's state
	#print "Now calling load() for every model element"
	store = first_store
	while store:
	    element = self.__factory.lookup (store.id())
	    #print element
	    if not element:
		raise ValueError, 'Element with id %d was created but can not be found anymore.' % id

	    element.load (store)
	    
	    store = store.next()

	# Do some things after the loading of the objects is done...
	#print self.__elements
	#save ('b.xml')
	#print "Now calling postload() for every model element"
	store = first_store
	while store:
	    element = self.__factory.lookup (store.id())
	    #print element
	    if not element:
		raise ValueError, 'Element with id %d was created but can not be found anymore.' % id

	    element.postload (store)
	    
	    store = store.next()

	doc.freeDoc ()

    #
    # Stuff for saving
    #
    def new(self, obj):
	node = None
	if isinstance (obj, UML.Element):
	    node = self.__node.newChild (Storage.NS, Storage.ELEMENT, None)
	    node.setProp (Storage.TYPE, obj.__class__.__name__)
	    node.setProp (Storage.ID, 'a' + str (obj.id))
	elif isinstance (obj, diacanvas.Canvas):
	    node = self.__node.newChild (Storage.NS, Storage.CANVAS, None)
	elif isinstance (obj, diacanvas.CanvasItem):
	    node = self.__node.newChild (Storage.NS, Storage.CANVAS_ITEM, None)
	    node.setProp (Storage.TYPE, obj.__class__.__name__)
	    node.setProp (Storage.CID, 'c' + str(obj.get_property('id')))
	return Storage (self.__factory, node, obj)

    def save_property (self, prop):
	prop_val = repr (self.__obj.get_property (prop))
	self.save_attribute (prop, prop_val)

    def save_attribute (self, name, obj):
	print 'saving', name, obj
	if isinstance (obj, UML.Element):
	    node = self.__node.newChild (Storage.NS, Storage.REFERENCE, None)
	    node.setProp (self.NAME, name)
	    node.setProp (self.REFID, 'a' + str(obj.id))
	else:
	    node = self.__node.newChild (Storage.NS, Storage.VALUE, None)
	    node.setProp (Storage.NAME, name)
	    node.setProp (Storage.PVALUE, str(obj))

    #
    # Stuff for loading
    #
    def next (self):
	'''Return the next node that is not a Value or a Reference.'''
	next = self.__node.next
	while next and next.name not in ( Storage.ELEMENT, Storage.CANVAS, Storage.CANVAS_ITEM ):
	    next = next.next
	if next:
	    return Storage (self.__factory, next)
	else:
	    return None

    def child (self):
	'''Return a child node that is not a Value or a Reference.'''
	child = self.__node.children
	while child and child.name not in ( Storage.ELEMENT, Storage.CANVAS, Storage.CANVAS_ITEM ):
	    child = child.next
	if child:
	    return Storage (self.__factory, child)
	else:
	    return None

    def type (self):
	cls = None
	type = None
	try:
	    type = self.__node.prop (Storage.TYPE)
	    if self.__node.name == Storage.ELEMENT:
		cls = getattr (UML, type)
	    elif self.__node.name == Storage.CANVAS_ITEM:
		cls = getattr (diagram, type)
	    else:
	        raise ValueError, 'Type should only be used on Elements and CanvasItems'
	except:
	    raise ValueError, 'Could not find class %s.' % type
	return cls

    def id (self):
	if self.__node.name != Storage.ELEMENT:
	    raise ValueError, 'ID can only be requested for Elements'
	return int (self.__node.prop (Storage.ID)[1:])

    def cid (self):
	if self.__node.name != Storage.CANVAS_ITEM:
	    raise ValueError, 'CID can only be requested for CanvasItems'
	return int (self.__node.prop (Storage.CID)[1:])

    def values (self):
	value = self.__node.children
	d = { }
	while value:
	    if value.name == Storage.VALUE:
		d[value.prop(Storage.NAME)] = value.prop(Storage.PVALUE)
	    value = value.next
	return d

    def references (self):
	'''Return a list of references for each item.'''
	ref = self.__node.children
	d = { }
	while ref:
	    if ref.name == Storage.REFERENCE:
		name = ref.prop(Storage.NAME)
		refid = ref.prop(Storage.REFID)
		if not refid[0] == 'a':
		    raise ValueError, 'Invalid ID for reference (%s)' % refid
		refid = int(refid[1:])
		refelem = self.__factory.lookup(refid)
		if d.has_key(name):
		    d[name].append (refelem)
		else:
		    d[name] = [ refelem ]
	    ref = ref.next
	return d

    def canvas (self):
	canvas = self.__node.children
	while canvas:
	    if canvas.name == Storage.CANVAS:
		return Storage (self.__factory, canvas)
	    canvas = canvas.next
	return None

    def canvas_items (self):
	'''From the code, return a dictionary of id: Storage items.
	'''
	item = self.__node.children
	d = { }
	while item:
	    if item.name == Storage.CANVAS_ITEM:
		d[int(item.prop(Storage.CID)[1:])] = Storage (self.__factory, \
							      item)
	    item = item.next
	return d

    def value(self, name):
	for valname, val in self.values().items():
	    if name == valname:
		return val
	raise ValueError, 'No value found with name %s' % name

    def reference(self, name):
	for refname, reflist in self.references().items():
	    if name == refname:
		return reflist
	raise ValueError, 'No reference found with name %s' % name

xml.initParser()
