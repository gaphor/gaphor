# vim: sw=4

# TODO: use xml.dom.minidom in stead of libxml2 (for compatibility and since libglade uses the python xml stuff too...)

import gaphor.UML as UML
import gaphor.diagram as diagram
import diacanvas
import types
import xml.dom.minidom as xml
import string

class StorageInfo:
    def __init__(self):
	self.factory = gaphorResource(UML.ElementFactory)
	self.itemfactory = gaphorResource(diagram.DiagramItemFactory)
	self.cid2item = { }
	self.doc=None

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
    #__cid_to_item_mapping = { }
    #doc = None

    def __init__(self, info=None, node=None, obj=None):
	object.__init__(self)
	self.__info = info or StorageInfo()
	self.__node = node
	self.__obj = obj
	
    def save (self, filename=None):
	'''Save the current model to @filename. If no filename is given,
	standard out is used.'''
	#doc = xml.newDoc ('1.0')
	self.__info.doc = xml.Document()
	#rootnode = doc.newChild (Storage.NS, 'Gaphor', None)
	rootnode = self.__info.doc.createElement('Gaphor')
	self.__info.doc.appendChild (rootnode)
	#rootnode.setProp ('version', '1.0')
	rootnode.setAttribute ('version', '1.0')
	store = Storage(self.__info, rootnode)
	for e in self.__info.factory.values():
	    #print 'Saving object', e
	    e.save(store.new(e))

	if not filename:
	    print document.toxml(indent='  ', newl='\n')
	else:
	    file = open (filename, 'w')
	    if not file:
		raise IOError, 'Could not open file `%s\'' % (filename)
	    #self.__doc.writexml (file, indent='', addindent='  ', newl='\n')
	    self.__info.doc.writexml (file)
	    file.close()
	#if not filename:
	#    filename = '-'

	#doc.saveFormatFileEnc (filename, 'UTF-8', 1)
	#doc.freeDoc ()

    def load (self, filename):
	'''Load a file and create a model if possible.
	Exceptions: IOError, ValueError.'''

	self.__info.cid2item = { }

	#doc = xml.parseFile (filename)
	self.__info.doc = xml.parse (filename)
	self.__info.doc.normalize()
	#print dir(self.__doc)

	# Now iterate over the tree and create every element in the
	# self.elements table.
	#rootnode = doc.children
	rootnode = self.__info.doc.firstChild
	#if rootnode.name != 'Gaphor':
	if rootnode.nodeName != 'Gaphor':
	    raise ValueError, 'File %s is not a Gaphor file.' % filename

	# Set store to the first child element of rootnode.
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
	    self.__info.itemfactory.set_next_id(cid + 1)
	    self.__info.cid2item[cid] = item
	else:
	    raise TypeError, 'CID %d is stored multiple times' % cid

    def lookup_item(self, cid):
	return self.__info.cid2item[cid]

    #
    # Stuff for saving
    #
    def new(self, obj):
	node = None
	if isinstance(obj, UML.Element):
	    #node = self.__node.newChild (Storage.NS, Storage.ELEMENT, None)
	    node = self.__info.doc.createElement(Storage.ELEMENT)
	    self.__node.appendChild(node)
	    #node.setProp (Storage.TYPE, obj.__class__.__name__)
	    node.setAttribute(Storage.TYPE, obj.__class__.__name__)
	    #node.setProp (Storage.ID, 'a' + str (obj.id))
	    node.setAttribute(Storage.ID, 'a' + str (obj.id))
	elif isinstance(obj, diacanvas.Canvas):
	    #node = self.__node.newChild (Storage.NS, Storage.CANVAS, None)
	    node = self.__info.doc.createElement(Storage.CANVAS)
	    self.__node.appendChild(node)
	elif isinstance(obj, diacanvas.CanvasItem):
	    #node = self.__node.newChild (Storage.NS, Storage.CANVAS_ITEM, None)
	    node = self.__info.doc.createElement(Storage.CANVAS_ITEM)
	    self.__node.appendChild(node)
	    #node.setProp (Storage.TYPE, obj.__class__.__name__)
	    node.setAttribute(Storage.TYPE, obj.__class__.__name__)
	    #node.setProp (Storage.CID, 'c' + str(obj.get_property('id')))
	    node.setAttribute(Storage.CID, 'c' + str(obj.get_property('id')))
	return Storage(self.__info, node, obj)

    def save_property (self, prop):
	prop_val = self.__obj.get_property (prop)
	self.save_attribute (prop, prop_val)

    def save_attribute (self, name, obj):
	print 'saving', name, obj
	if isinstance (obj, UML.Element):
	    #node = self.__node.newChild (Storage.NS, Storage.REFERENCE, None)
	    node = self.__info.doc.createElement(Storage.REFERENCE)
	    self.__node.appendChild(node)
	    #node.setProp (self.NAME, name)
	    node.setAttribute (self.NAME, name)
	    #node.setProp (self.REFID, 'a' + str(obj.id))
	    node.setAttribute (self.REFID, 'a' + str(obj.id))
	elif isinstance (obj, diacanvas.CanvasItem):
	    #node = self.__node.newChild (Storage.NS, Storage.REFERENCE, None)
	    node = self.__info.doc.createElement(Storage.REFERENCE)
	    self.__node.appendChild(node)
	    #node.setProp (self.NAME, name)
	    node.setAttribute (self.NAME, name)
	    #node.setProp (self.REFID, 'c' + str(obj.get_property('id')))
	    node.setAttribute (self.REFID, 'c' + str(obj.get_property('id')))
	else:
	    #node = self.__node.newChild (Storage.NS, Storage.VALUE, None)
	    node = self.__info.doc.createElement(Storage.VALUE)
	    self.__node.appendChild(node)
	    node.setAttribute (Storage.NAME, name)
	    if isinstance(obj, types.StringType):
		cdata = self.__info.doc.createCDATASection(obj)
		node.appendChild(cdata)
	    else:
		#text = self.__doc.createTextNode(str(obj))
		#node.appendChild(text)
		node.setAttribute (Storage.PVALUE, str(obj))

    #
    # Stuff for loading
    #
    def next (self):
	'''Return the next node that is not a Value or a Reference.'''
	#next = self.__node.next
	next = self.__node.nextSibling
	while next and next.nodeName not in ( Storage.ELEMENT, Storage.CANVAS, Storage.CANVAS_ITEM ):
	    #next = next.next
	    next = next.nextSibling
	if next:
	    return Storage(self.__info, next)
	else:
	    return None

    def child (self):
	'''Return a child node that is not a Value or a Reference.'''
	#child = self.__node.children
	child = self.__node.firstChild
	while child and child.nodeName not in ( Storage.ELEMENT, Storage.CANVAS, Storage.CANVAS_ITEM ):
	    #child = child.next
	    child = child.nextSibling
	if child:
	    return Storage(self.__info, child)
	else:
	    return None

    def type (self):
	cls = None
	type = None
	try:
	    #type = self.__node.prop (Storage.TYPE)
	    type = self.__node.getAttribute(Storage.TYPE)
	    if self.__node.nodeName == Storage.ELEMENT:
		cls = getattr (UML, type)
	    elif self.__node.nodeName == Storage.CANVAS_ITEM:
		cls = getattr (diagram, type)
	    else:
	        raise ValueError, 'Type should only be used on Elements and CanvasItems'
	except:
	    raise ValueError, 'Could not find class %s.' % type
	return cls

    def id (self):
	if self.__node.nodeName != Storage.ELEMENT:
	    raise ValueError, 'ID can only be requested for Elements'
	#return int (self.__node.prop (Storage.ID)[1:])
	return int (self.__node.getAttribute(Storage.ID)[1:])

    def cid (self):
	if self.__node.nodeName != Storage.CANVAS_ITEM:
	    raise ValueError, 'CID can only be requested for CanvasItems'
	#return int (self.__node.prop (Storage.CID)[1:])
	return int (self.__node.getAttribute(Storage.CID)[1:])

    def values (self):
	#value = self.__node.children
	value = self.__node.firstChild
	d = { }
	while value:
	    #if value.name == Storage.VALUE:
	    if value.nodeName == Storage.VALUE:
		#d[value.prop(Storage.NAME)] = value.prop(Storage.PVALUE)
		#d[value.attributes.get(Storage.NAME).nodeValue] = value.attributes.get(Storage.PVALUE).nodeValue
		data = value.getAttribute(Storage.PVALUE)
		print 'Data (1) is', data
		if not data:
		    print 'Search for a CDATA section'
		    data = value.firstChild
		    while data:
			print data.nodeType, data.nodeName, data.nodeValue, data.attributes
			if data.nodeType == xml.Node.TEXT_NODE:
			    data = data.nodeValue
			    if data is None:
				data = ''
			    break
			data = data.nextSibling
		print 'Value data:', data
		d[value.getAttribute(Storage.NAME)] = data
	    value = value.nextSibling
	return d

    def references (self):
	'''Return a dictionary of references for each item.
	A list is created for every reference name.'''
	#ref = self.__node.children
	ref = self.__node.firstChild
	d = { }
	while ref:
	    #if ref.name == Storage.REFERENCE:
	    if ref.nodeName == Storage.REFERENCE:
		refelem = None
		#name = ref.prop(Storage.NAME)
		name = ref.getAttribute(Storage.NAME)
		#refid = ref.prop(Storage.REFID)
		refid = ref.getAttribute(Storage.REFID)
		if refid[0] == 'c':
		    key = int(refid[1:])
		    # We have the possibility that a canvas item is not yet
		    # created, so we should be cautious with assigning refelems
		    if self.__info.cid2item.has_key(key):
			refelem = self.__info.cid2item[key]
		elif refid[0] == 'a':
		    key = int(refid[1:])
		    refelem = self.__info.factory.lookup(key)
		elif refid == 'None':
		    pass
		else:
		    raise ValueError, 'Invalid ID for reference (%s)' % refid

		if refelem:
		    if d.has_key(name):
			d[name].append (refelem)
		    else:
			d[name] = [ refelem ]
	    #ref = ref.next
	    ref = ref.nextSibling
	return d

    def canvas (self):
	#canvas = self.__node.children
	canvas = self.__node.firstChild
	while canvas:
	    #if canvas.name == Storage.CANVAS:
	    if canvas.nodeName == Storage.CANVAS:
		return Storage(self.__info, canvas)
	    #canvas = canvas.next
	    canvas = canvas.nextSibling
	return None

    def canvas_items (self):
	'''From the code, return a dictionary of id: Storage items.
	'''
	#item = self.__node.children
	item = self.__node.firstChild
	d = { }
	while item:
	    #if item.name == Storage.CANVAS_ITEM:
	    if item.nodeName == Storage.CANVAS_ITEM:
		s = Storage(self.__info, item)
		d[s.cid()] = s
	    #item = item.next
	    item = item.nextSibling
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

