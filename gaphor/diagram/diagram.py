# vim: sw=4
'''diagram.py
This module contains a model elements (!) Diagram which is the abstract
repreesentation of a UML diagram.'''

import UML, diacanvas, diagramitems, types, itemstorage

diagram2UML = {
	diagramitems.Actor: UML.Actor,
	diagramitems.Comment: UML.Comment,
	diagramitems.UseCase: UML.UseCase,
	diagramitems.CommentLine: None,
	diagramitems.Generalization: None
}

class Diagram(UML.Namespace):
    _attrdef = { 'canvas': ( None, diacanvas.Canvas ),
		 # Translation table used to keep relations between the
		 # old object's cid and the new objects 
    		 'transtable': ( None, types.DictType ) } 

    def __init__(self, id):
	UML.Namespace.__init__(self, id)
        self.canvas = diacanvas.Canvas()
	self.canvas.set_property ("allow_undo", 1)
	#Diagram._diagrams.append (weakref.ref (self))

    def create (self, type, pos=(0, 0), subject=None):
	item = self.canvas.root.add(type)
	if not subject:
	    uml_type = diagram2UML[type]
	    if uml_type is not None:
		print 'Setting new subject of type', uml_type
		factory = UML.ElementFactory ()
		subject = factory.create (uml_type)
		if issubclass (uml_type, UML.Namespace):
		    subject.namespace = self.namespace
		item.set_subject(subject)
	else:
	    print 'Setting existing subject', subject
	    item.set_subject(subject)
	item.move(pos[0], pos[1])
	return item

    def save(self, parent, ns):
        node = UML.Namespace.save (self, parent, ns)
	canvas = node.newChild (ns, 'Canvas', None)
	# Save attributes of the canvas:
	for a in [ 'extents', 'static_extents', 'snap_to_grid',
		   'grid_int_x', 'grid_int_y', 'grid_ofs_x',
		   'grid_ofs_y', 'snap_to_grid', 'grid_color', 'grid_bg' ]:
	    canvas.setProp (a, repr (self.canvas.get_property (a)))

	def save_item (item, parent, ns):
	    node = itemstorage.save (item, parent, ns)

	    if isinstance (item, diacanvas.CanvasGroupable):
		iter = item.get_iter ()
		if iter:
		    while item.value (iter):
		        save_item (item.value (iter), node, ns)
			item.next(iter);

	save_item (self.canvas.root, canvas, ns)
	return node

    def load (self, node):
	print 'Doing Namespace'
        UML.Namespace.load (self, node)
	print 'Namespace done'
	self.transtable = { } # table to translate 'cid' to object

	# First create all objects:
	canvasnode = node.children
	while canvasnode and canvasnode.name != 'Canvas':
	    canvasnode = canvasnode.next
	assert canvasnode != None

	self.canvas.set_property ("allow_undo", 0)

	# Load canvas properties:
	for a in [ 'extents', 'static_extents', 'snap_to_grid',
		   'grid_int_x', 'grid_int_y', 'grid_ofs_x',
		   'grid_ofs_y', 'snap_to_grid', 'grid_color', 'grid_bg' ]:
	    attr = canvasnode.prop (a)
	    if attr:
		self.canvas.set_property (a, eval (attr))
	    
	rootnode = canvasnode.children
	while rootnode.name != 'CanvasItem':
	    next = rootnode.next
	    rootnode.unlinkNode ()
	    rootnode.freeNode ()
	    rootnode = next

	if not rootnode or rootnode.prop ('type') != 'CanvasGroup':
	    raise ValueError, 'The Canvas tag should contain a CanvasItem with type CanvasGroup, but none was found.'
	    
	def load_item (item, node):
	    itemstorage.load (item, node)

	    # Create child items in case of a canvas group...
	    #if isinstance (item, diacanvas.CanvasGroupable):
	    childnode = node.children
	    while childnode:
		if childnode.name == 'CanvasItem':
		    typestr = childnode.prop ('type')
		    type = getattr (diagramitems, typestr)
		    childitem = item.add (type)
		    load_item (childitem, childnode)
		    childnode = childnode.next
		# Remove the text node, we don't use it anyway
		elif childnode.name == 'text':
		    next = childnode.next
		    childnode.unlinkNode ()
		    childnode.freeNode ()
		    childnode = next
		else:
		    raise ValueError, 'Invalid node type %s, should be CanvasItem' % childnode
	
	load_item (self.canvas.root, rootnode)
	self.transtable = itemstorage.get_transtable ()

    def postload (self, node): 
        '''We use postload() to connect objects to each other. This can not
	be done in the load() method, since objects can change their size and
	contents after we have connected to them (since they are not yet
	initialized).'''

	# All objects are loaded and the fields are properly set.
	self.canvas.update_now ()

        itemstorage.set_transtable (self.transtable)

	canvasnode = node.children
	while canvasnode and canvasnode.name != 'Canvas':
	    canvasnode = canvasnode.next
	assert canvasnode != None
	
	rootnode = canvasnode.children
	assert rootnode.name == 'CanvasItem'
	assert rootnode.prop ('type') == 'CanvasGroup'
	
	def postload_item (item, node):
	    itemstorage.postload (item, node)

	    # Do examine child objects:
	    if isinstance (item, diacanvas.CanvasGroupable):
	        childnode = node.children
		iter = item.get_iter()
		while childnode:
		    if childnode.name == 'CanvasItem':
			postload_item (item.value(iter), childnode)
			item.next(iter)
		    childnode = childnode.next
	    
	postload_item (self.canvas.root, rootnode)
	del self.transtable
	itemstorage.flush_transtable ()
	self.canvas.set_property ("allow_undo", 1)
	self.canvas.update_now ()

