# vim: sw=4

# TODO: use xml.dom.minidom in stead of libxml2 (for compatibility and since libglade uses the python xml stuff too...)

import gaphor.UML as UML
import gaphor.diagram as diagram
import diacanvas
import types
import xml.dom.minidom as xml
import string

def get_id(node):
    return int (node.getAttribute(Storage.ID)[1:])

def get_cid(node):
    return int (node.getAttribute(Storage.CID)[1:])

class StorageNode:
    def __init__(self, parent):
	self.__parent = parent

    def save(self, name, obj):
	doc = self.__parent.ownerDocument
	if isinstance (obj, UML.Element):
	    node = doc.createElement(Storage.REFERENCE)
	    self.__parent.appendChild(node)
	    node.setAttribute (Storage.NAME, name)
	    node.setAttribute (Storage.REFID, 'a' + str(obj.id))
	elif isinstance(obj, diacanvas.Canvas):
	    node = doc.createElement(Storage.CANVAS)
	    self.__parent.appendChild(node)
	    obj.save(StorageNode(node).save)
	elif isinstance(obj, diacanvas.CanvasItem):
	    # We can store a reference here, or a subitem
	    if not name: # subitem
		node = doc.createElement(Storage.CANVAS_ITEM)
		self.__parent.appendChild(node)
		node.setAttribute(Storage.TYPE, obj.__class__.__name__)
		node.setAttribute(Storage.CID, 'c'+str(obj.get_property('id')))
		obj.save(StorageNode(node).save)
	    else: # reference
		node = doc.createElement(Storage.REFERENCE)
		self.__parent.appendChild(node)
		node.setAttribute (Storage.NAME, name)
		node.setAttribute (Storage.REFID, 'c'+str(obj.get_property('id')))
	else:
	    node = doc.createElement(Storage.VALUE)
	    self.__parent.appendChild(node)
	    node.setAttribute (Storage.NAME, name)
	    if isinstance(obj, types.StringType):
		cdata = doc.createCDATASection(obj)
		node.appendChild(cdata)
	    else:
		node.setAttribute (Storage.PVALUE, str(obj))

    def load(self, element, factory, cid2item):
	for node in self.__parent.childNodes:
	    #if node.nodeName not in ( Storage.VALUE, Storage.REFERENCE, Storage.CANVAS, Storage.CANVAS_ITEM )
	    if node.nodeName == Storage.VALUE:
		name = node.getAttribute(Storage.NAME)
		# If we do not have a value attribute, return the CDATA section
		value = node.getAttribute(Storage.PVALUE)
		if not value:
		    text_node = node.firstChild
		    if text_node and text_node.nodeType == xml.Node.TEXT_NODE:
			value = text_node.nodeValue
		    else:
			value = ''
		element.load(name, value)
	    elif node.nodeName == Storage.REFERENCE:
		name = node.getAttribute(Storage.NAME)
		refid = node.getAttribute(Storage.REFID)
		if refid[0] == 'c':
		    key = int(refid[1:])
		    # We have the possibility that a canvas item is not yet
		    # created, so we should be cautious with assigning refelems
		    if cid2item.has_key(key):
			value = cid2item[key]
		elif refid[0] == 'a':
		    key = int(refid[1:])
		    value = factory.lookup(key)
		elif refid == 'None':
		    value = None
		else:
		    raise ValueError, 'Invalid ID for reference (%s)' % refid
		element.load(name, value)
	    elif node.nodeName == Storage.CANVAS:
		# For the canvas node, load all sub nodes:
		StorageNode(node).load(element.canvas, factory, cid2item)
	    elif node.nodeName == Storage.CANVAS_ITEM:
		cid = get_cid(node)
		item = cid2item[cid]
		StorageNode(node).load(item, factory, cid2item)
	    else:
		raise ValueError, '%s node may only contain Value, Reference, Canvas and CanvasItem nodes' % self.__parent.nodeName

    def postload (self, element, factory, cid2item):
	for node in self.__parent.childNodes:
	    if node.nodeName == Storage.CANVAS:
		print 'CANVAS'
		StorageNode(node).postload(element.canvas, factory, cid2item)
		#element.postload()
	    elif node.nodeName == Storage.CANVAS_ITEM:
		cid = get_cid(node)
		item = cid2item[cid]
		print 'CANVAS_ITEM', item
		StorageNode(node).load(item, factory, cid2item)
		item.postload()
	print 'pl:', element
	element.postload()

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

    def __init__(self, info=None, node=None, obj=None):
	object.__init__(self)
	
    def save (self, filename=None):
	'''Save the current model to @filename. If no filename is given,
	standard out is used.'''
	doc = xml.Document()
	rootnode = doc.createElement('Gaphor')
	doc.appendChild (rootnode)
	rootnode.setAttribute ('version', '1.0')
	factory = GaphorResource(UML.ElementFactory)

	for e in factory.values():
	    node = doc.createElement(Storage.ELEMENT)
	    rootnode.appendChild(node)
	    node.setAttribute(Storage.TYPE, e.__class__.__name__)
	    node.setAttribute(Storage.ID, 'a' + str (e.id))
	    e.save(StorageNode(node).save)

	if not filename:
	    print document.toxml(indent='  ', newl='\n')
	else:
	    file = open (filename, 'w')
	    if not file:
		raise IOError, 'Could not open file `%s\'' % (filename)
	    try:
		doc.writexml (file)
	    finally:
		file.close()

    def load (self, filename):
	'''Load a file and create a model if possible.
	Exceptions: IOError, ValueError.'''

	def create_canvas_items(node, item, cid2item):
	    for child in node.childNodes:
		if child.nodeName == Storage.CANVAS_ITEM:
		    type = child.getAttribute(Storage.TYPE)
		    id = int(child.getAttribute(Storage.CID)[1:])
		    cls = getattr(diagram, type)
		    child_item = cls()
		    child_item.set_property('id', id)
		    cid2item[id] = child_item
		    child_item.set_property('parent', item)
		    create_canvas_items(child, child_item, cid2item)

	cid2item = dict()
	factory = GaphorResource(UML.ElementFactory)

	doc = xml.parse (filename)
	doc.normalize()
	#print dir(self.__doc)

	# Now iterate over the tree and create every element in the
	# self.elements table.
	#rootnode = doc.children
	rootnode = doc.documentElement
	if rootnode.nodeName != 'Gaphor':
	    raise ValueError, 'File %s is not a Gaphor file.' % filename

	# Create Element's
	for node in rootnode.childNodes:
	    if node.nodeName != Storage.ELEMENT:
		raise ValueError, 'Gaphor node may contain only Element nodes'
	    name = node.getAttribute(Storage.TYPE)
	    type = getattr (UML, name)
	    element = factory.create_as (type, get_id(node))
	    # Check for a Canvas child node, if one is found, create
	    # CanvasItems.
	    if name == 'Diagram':
		for child in node.childNodes:
		    if child.nodeName == Storage.CANVAS:
			assert isinstance (element, UML.Diagram)
			create_canvas_items(child, element.canvas.root, cid2item)

	    node = node.nextSibling

	# Let the elements load their variables
	for node in rootnode.childNodes:
	    element = factory.lookup (get_id (node))
	    StorageNode(node).load(element, factory, cid2item)

	# Postprocess the element, give them a chance to clean up etc.
	for node in rootnode.childNodes:
	    element = factory.lookup (get_id (node))
	    StorageNode(node).postload(element, factory, cid2item)

	return

	first_store = Storage(self.__info, rootnode)
	first_store = first_store.child()
	#first_store = first_store.firstChild

	# Create plain elements in the factory
	#print 'first_store =', first_store.__dict__
	store = first_store
	while store:

	    #print 'Creating object of type', store.type()
	    type = store.type()
	    if not issubclass(type, UML.Element):
		raise ValueError, 'Not an UML.Element'

	    self.__info.factory.create_as (type, store.id())

	    store = store.next()

	# Second step: call Element.load() for every object in the element hash.
	# We also provide the XML node, so it can recreate it's state
	#print "Now calling load() for every model element"
	store = first_store
	while store:
	    element = self.__info.factory.lookup (store.id())
	    #print element
	    if not element:
		raise ValueError, 'Element with id %d was created but can not be found anymore.' % store.id()

	    element.load (store)
	    
	    store = store.next()

	# Do some things after the loading of the objects is done...
	#print self.__elements
	#save ('b.xml')
	#print "Now calling postload() for every model element"
	store = first_store
	while store:
	    element = self.__info.factory.lookup (store.id())
	    #print element
	    if not element:
		raise ValueError, 'Element with id %d was created but can not be found anymore.' % store.id()

	    element.postload (store)
	    
	    store = store.next()

	#doc.freeDoc ()

    def add_cid_to_item_mapping(self, cid, item):
	if not self.__info.cid2item.has_key(cid):
	    #self.__info.itemfactory.set_next_id(cid + 1)
	    self.__info.cid2item[cid] = item
	else:
	    raise TypeError, 'CID %d is stored multiple times' % cid

    def lookup_item(self, cid):
	return self.cid2item[cid]

