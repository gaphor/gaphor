# vim: sw=4

# TODO: use xml.dom.minidom in stead of libxml2 (for compatibility and since libglade uses the python xml stuff too...)

import gaphor.UML as UML
import gaphor.diagram as diagram
import diacanvas
import types
import xml.dom.minidom as dom
import string
import gtk
import gc

NS=None
ELEMENT='Element'
CANVAS='Canvas'
CANVAS_ITEM='CanvasItem'
VALUE='Value'
REFERENCE='Reference'
NAME='name'
TYPE='type'
ID='id'
REFID='refid'
PVALUE='value'

def save (filename=None):
    '''Save the current model to @filename. If no filename is given,
    standard out is used.'''
    doc = dom.Document()
    rootnode = doc.createElement('Gaphor')
    doc.appendChild (rootnode)
    rootnode.setAttribute ('version', '1.1')
    factory = GaphorResource(UML.ElementFactory)

    class Saver:
	def __init__(self, parent):
	    self.__parent = parent

	def save(self, name, obj):
	    doc = self.__parent.ownerDocument
	    if isinstance (obj, UML.Element):
		node = doc.createElement(REFERENCE)
		self.__parent.appendChild(node)
		node.setAttribute (NAME, name)
		#node.setAttribute (REFID, ELEMENT_PREFIX + str(obj.id))
		node.setAttribute (REFID, str(obj.id))
	    elif isinstance(obj, diacanvas.Canvas):
		node = doc.createElement(CANVAS)
		self.__parent.appendChild(node)
		obj.save(Saver(node).save)
	    elif isinstance(obj, diacanvas.CanvasItem):
		# We can store a reference here, or a subitem
		if not name: # subitem
		    node = doc.createElement(CANVAS_ITEM)
		    self.__parent.appendChild(node)
		    node.setAttribute(TYPE, obj.__class__.__name__)
		    node.setAttribute(ID, str(obj.get_property('id')))
		    obj.save(Saver(node).save)
		else: # reference
		    node = doc.createElement(REFERENCE)
		    self.__parent.appendChild(node)
		    node.setAttribute (NAME, name)
		    node.setAttribute (REFID, str(obj.get_property('id')))
	    else:
		node = doc.createElement(VALUE)
		self.__parent.appendChild(node)
		node.setAttribute (NAME, name)
		if isinstance(obj, types.StringType):
		    # Ensure that a CDATA section does not contain ']]>', since
		    # some XML parsers have problems with it...
		    cdata = doc.createCDATASection(obj.replace(']]>', ']] >'))
		    node.appendChild(cdata)
		else:
		    node.setAttribute (PVALUE, str(obj))

    for e in factory.values():
	node = doc.createElement(ELEMENT)
	rootnode.appendChild(node)
	node.setAttribute(TYPE, e.__class__.__name__)
	#node.setAttribute(ID, ELEMENT_PREFIX + str (e.id))
	node.setAttribute(ID, str (e.id))
	e.save(Saver(node).save)

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

def _load (doc, factory):
    '''Load a file and create a model if possible.
    Exceptions: IOError, ValueError.'''

    version = '1.1'
    id2element = dict()

    def get_id(node):
	""" retrieve the ID from a node. in case of old gaphor files,
	CanvasItem's have a 'cid' in stead of 'id'.
	"""
	id = node.getAttribute(ID)
	# Fallback for old gaphor models:
	if not id and version == '1.0':
	    id = node.getAttribute('cid')
	return id

    def load_canvas_items(node, item):
	for child in node.childNodes:
	    if child.nodeName == CANVAS_ITEM:
		type = child.getAttribute(TYPE)
		id = get_id(child) #child.getAttribute(ID)
		cls = getattr(diagram, type)
		child_item = cls()
		child_item.set_property('id', id)
		id2element[id] = child_item
		child_item.set_property('parent', item)
		load_canvas_items(child, child_item)

    def load_node(parent, element):
	"""load_node is a recursive function that is used to set values
	and references from one model element to another.
	"""
	for node in parent.childNodes:
	    #if node.nodeName not in ( VALUE, REFERENCE, CANVAS, CANVAS_ITEM )
	    if node.nodeName == VALUE:
		name = node.getAttribute(NAME)
		#print 'value name =', name, element
		# If we do not have a value attribute, return the CDATA section
		value = node.getAttribute(PVALUE)
		if not value:
		    text_node = node.firstChild
		    if text_node and text_node.nodeType == dom.Node.TEXT_NODE:
			value = text_node.nodeValue
		    else:
			value = ''
		#print 'value', element, name, value
		element.load(name, value)
	    elif node.nodeName == REFERENCE:
		name = node.getAttribute(NAME)
		refid = node.getAttribute(REFID)
		if id2element.has_key(refid):
		    value = id2element[refid]
		else:
		    raise ValueError, 'Invalid ID for reference (%s)' % refid
		#print 'refer', element, name, value
		element.load(name, value)
	    elif node.nodeName == CANVAS:
		# For the canvas node, load all sub nodes:
		load_node(node, element.canvas)
	    elif node.nodeName == CANVAS_ITEM:
		id = get_id(node) #node.getAttribute(ID)
		item = id2element[id]
		#print 'found item:', item, id
		load_node(node, item)
	    else:
		raise ValueError, '%s node may only contain Value, Reference, Canvas and CanvasItem nodes' % parent.nodeName

    def postload_node (parent, element):
        """Call postload() on all created elements. The postload is done
	in a reverse order (first the child, then the parent items).
	"""
	for node in parent.childNodes:
	    if node.nodeName == CANVAS:
		postload_node(node, element.canvas)
	    elif node.nodeName == CANVAS_ITEM:
		id = get_id(node) #node.getAttribute(ID)
		item = id2element[id]
		postload_node(node, item)
	element.postload()

    doc.normalize()

    rootnode = doc.documentElement
    if rootnode.nodeName != 'Gaphor':
	raise ValueError, 'File %s is not a Gaphor file.' % filename

    version = rootnode.getAttribute('version')

    # Create Element's
    for node in rootnode.childNodes:
	if node.nodeName != ELEMENT:
	    raise ValueError, 'Gaphor node may contain only Element nodes'
	name = node.getAttribute(TYPE)
	id = node.getAttribute(ID)

	type = getattr (UML, name)
	element = factory.create_as (type, id)
	id2element[id] = element
	# For a Diagram, create CanvasItem's.
	if name == 'Diagram':
	    for child in node.childNodes:
		if child.nodeName == CANVAS:
		    assert isinstance (element, UML.Diagram)
		    load_canvas_items(child, element.canvas.root)

    # Let the elements load their variables
    for node in rootnode.childNodes:
	element = factory.lookup (node.getAttribute(ID))
	load_node(node, element)

    # Postprocess the element, give them a chance to clean up etc.
    diagrams = []
    for node in rootnode.childNodes:
	element = factory.lookup (node.getAttribute(ID))
	element.postload()
	if isinstance (element, UML.Diagram):
	    diagrams.append((node, element))

    for node, element in diagrams:
	postload_node(node, element)

def load (filename):
    '''Load a file and create a model if possible.
    Exceptions: GaphorError.'''
    try:
	doc = dom.parse (filename)
    except Exception, e:
	raise GaphorError, 'File %s is probably no valid XML.' % filename

    try:
    	# For some reason, loading the model in a temp. factory will
	# cause DiaCanvas2 to keep a idle handler around... This should
	# be fixed in DiaCanvas2 ASAP.
	#factory = UML.ElementFactory()
	#_load(doc, factory)
	#gc.collect()
	#factory.flush()
	#del factory
	#gc.collect()
	#print '===================================== pre load succeeded =='
	factory = GaphorResource(UML.ElementFactory)
	factory.flush()
    	_load(doc, factory)
	gc.collect()
    except Exception, e:
	log.info('file %s could not be loaded' % filename)
	raise GaphorError, 'Could not load file %s (%s)' % (filename, e)

def verify (filename):
    """
    Try to load the file. If loading succeeded, this file is probably a valid
    Gaphor file.
    """
    try:
	doc = dom.parse (filename)
    except Exception, e:
	log.info('File %s is probably no valid XML.' % filename)
	return False

    factory = UML.ElementFactory()
    try:
	_load(doc, factory)
    except Exception, e:
	log.info('File %s could not be loaded' % filename)
	return False

    return True
