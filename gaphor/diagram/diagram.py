# vim: sw=4
'''diagram.py
This module contains a model elements (!) Diagram which is the abstract
repreesentation of a UML diagram.'''

import UML, diacanvas, types
from usecase import UseCase

diagram2UML = {
#	Actor: UML.Actor,
#	Comment: UML.Comment,
	UseCase: UML.UseCase
#	CommentLine: None,
#	Generalization: None
}

class Diagram(UML.Namespace):
    _attrdef = { 'canvas': ( None, diacanvas.Canvas ),
		 # Translation table used to keep relations between the
		 # old object's cid and the new objects 
    		 'transtable': ( None, types.DictType ) } 
    _savable_canvas_properties = [ 'extents', 'static_extents',
	    'snap_to_grid', 'grid_int_x', 'grid_int_y', 'grid_ofs_x',
	    'grid_ofs_y', 'snap_to_grid', 'grid_color', 'grid_bg' ]
    _savable_root_item_properties = [ 'affine', ]

    def __init__(self, id):
	UML.Namespace.__init__(self, id)
        self.canvas = diacanvas.Canvas()
	self.canvas.set_property ("allow_undo", 1)

    def create (self, type, pos=(0, 0), subject=None):
        '''TODO: this function should be removed from the diagram and put
	in its own ElementFactory, or should it?'''
	#item = diacanvas.dia_canvas_item_create (type)
	item = type()
	self.canvas.root.add(item)
	if not subject:
	    uml_type = diagram2UML[type]
	    if uml_type is not None:
		#print 'Setting new subject of type', uml_type
		factory = UML.ElementFactory ()
		subject = factory.create (uml_type)
		if issubclass (uml_type, UML.Namespace):
		    print 'Diagram.create:', self.namespace
		    subject.namespace = self.namespace
		    print '...', subject.namespace
		item.set_property ('subject', subject)
	else:
	    #print 'Setting existing subject', subject
	    item.set_property ('subject', subject)
	item.move(pos[0], pos[1])
	return item

    def save(self, store):
	# Save the diagram attributes, but not the canvas
	self_canvas = self.canvas
	del self.__dict__['canvas']
	node = UML.Namespace.save (self, store)
	self.__dict__['canvas'] = self_canvas
	del self_canvas

	# Save attributes of the canvas:
	canvas_store = store.new (self.canvas)
	for prop in Diagram._savable_canvas_properties:
	    canvas_store.save_property(prop)

	root_store = store.new (self.canvas.root)
	for prop in Diagram._savable_root_item_properties:
	    root_store.save_property(prop)

	# Save child items:
	for item in self.canvas.root.children:
	    item.save(root_store.new(item))

    def load (self, factory, node):
	#print 'Doing Namespace'
        UML.Namespace.load (self, factory, node)
	#print 'Namespace done'
	self.transtable = { } # table to translate 'cid' to object

	# First create all objects:
	canvasnode = node.children
	while canvasnode and canvasnode.name != 'Canvas':
	    canvasnode = canvasnode.next
	assert canvasnode != None

	self.canvas.set_property ("allow_undo", 0)

	# Load canvas properties:
	#for a in [ 'extents', 'static_extents', 'snap_to_grid',
	#	   'grid_int_x', 'grid_int_y', 'grid_ofs_x',
	#	   'grid_ofs_y', 'snap_to_grid', 'grid_color', 'grid_bg' ]:
	#    attr = canvasnode.prop (a)
	#    if attr:
	#	self.canvas.set_property (a, eval (attr))
	value = canvasnode.children
	while value:
	    if value.name == 'Value':
	        name = value.prop ('name')
		self.canvas.set_property (name, eval (value.prop ('value')))
	    value = value.next

	rootnode = canvasnode.children
	while rootnode.name != 'CanvasItem':
	    next = rootnode.next
	    rootnode.unlinkNode ()
	    rootnode.freeNode ()
	    rootnode = next

	if not rootnode or rootnode.prop ('type') != 'CanvasGroup':
	    raise ValueError, 'The Canvas tag should contain a CanvasItem with type CanvasGroup, but none was found.'
	    
	def load_item (item, node):
	    itemstorage.load (item, factory, node)

	    # Create child items in case of a canvas group...
	    # if isinstance (item, diacanvas.CanvasGroupable):
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
		    childnode = childnode.next
		#    raise ValueError, 'Invalid node type %s, should be CanvasItem' % childnode
	
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

