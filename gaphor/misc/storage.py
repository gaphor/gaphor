# vim: sw=4

import UML
import diagram
import diacanvas
import types

class Storage(object):
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

    def __init__(self, factory, ns, node, obj=None):
	object.__init__(self)
	self.__factory = factory
	self.__ns = ns
	self.__node = node
	self.__obj = obj

    #
    # Stuff for saving
    #
    def new(self, obj):
	node = None
	if isinstance (obj, UML.Element):
	    node = self.__node.newChild (self.__ns, Storage.ELEMENT, None)
	    node.setProp (Storage.TYPE, obj.__class__.__name__)
	    node.setProp (Storage.ID, 'a' + str (obj.id))
	elif isinstance (obj, diacanvas.Canvas):
	    node = self.__node.newChild (self.__ns, Storage.CANVAS, None)
	elif isinstance (obj, diacanvas.CanvasItem):
	    node = self.__node.newChild (self.__ns, Storage.CANVAS_ITEM, None)
	    node.setProp (Storage.TYPE, obj.__class__.__name__)
	    node.setProp (Storage.CID, 'c' + str(obj.get_property('id')))
	return Storage (self.__factory, self.__ns, node, obj)

    def save_property (self, prop):
	prop_val = repr (self.__obj.get_property (prop))
	self.save (prop, prop_val)

    def save (self, name, obj):
	print 'saving', name, obj
	if isinstance (obj, UML.Element):
	    node = self.__node.newChild (self.__ns, Storage.REFERENCE, None)
	    node.setProp (self.NAME, name)
	    node.setProp (self.REFID, 'a' + str(obj.id))
	else:
	    node = self.__node.newChild (self.__ns, Storage.VALUE, None)
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
	    return Storage (self.__factory, self.__ns, next)
	else:
	    return None

    def child (self):
	'''Return a child node that is not a Value or a Reference.'''
	child = self.__node.children
	while child and child.name not in ( Storage.ELEMENT, Storage.CANVAS, Storage.CANVAS_ITEM ):
	    child = child.next
	if child:
	    return Storage (self.__factory, self.__ns, child)
	else:
	    return None

    def type (self):
	cls = None
	type = None
	try:
	    type = self.__node.prop (Storage.TYPE)
	    if self.__node.name == Storage.ELEMENT:
		if type == 'Diagram':
		    cls = getattr (diagram, type)
		else:
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
	factory = UML.ElementFactory()
	ref = self.__node.children
	d = { }
	while ref:
	    if ref.name == Storage.REFERENCE:
		name = ref.prop(Storage.NAME)
		refid = ref.prop(Storage.REFID)
		if not refid[0] == 'a':
		    raise ValueError, 'Invalid ID for reference (%s)' % refid
		refid = int(refid[1:])
		refelem = factory.lookup(refid)
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
		return Storage (self.__factory, self.__ns, canvas)
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
							      self.__ns, item)
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
