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
	diagramitems.Generalization: UML.Generalization
}

class Diagram(UML.Namespace):
    _attrdef = { 'canvas': ( None, diacanvas.Canvas ),
		 # Translation table used to keep relations between the
		 # old object's cid and the new objects 
    		 'transtable': ( None, types.DictType ) } 

    def __init__(self):
	UML.Namespace.__init__(self)
        self.canvas = diacanvas.Canvas()
	self.canvas.set_property ("allow_undo", 1)
	#Diagram._diagrams.append (weakref.ref (self))

    def create_item (self, type, pos=(0, 0), subject=None):
	item = self.canvas.root.add(type)
	if not subject:
	    uml_type = diagram2UML[type]
	    if uml_type is not None:
		print 'Setting new subject of type', uml_type
		subject = uml_type()
		if issubclass (uml_type, UML.Namespace):
		    subject.namespace = self.namespace
		item.set_subject(subject)
	else:
	    print 'Setting existing subject', subject
	    item.set_subject(subject)
	item.move(pos[0], pos[1])
	return item

    def save(self, document, parent):
        node = UML.Namespace.save (self, document, parent)
	canvas = document.createElement ('Canvas')
	node.appendChild (canvas)
	# Save attributes of the canvas:
	for a in [ 'extents', 'static_extents', 'snap_to_grid',
		   'grid_int_x', 'grid_int_y', 'grid_ofs_x',
		   'grid_ofs_y', 'snap_to_grid', 'grid_color', 'grid_bg' ]:
	    canvas.setAttribute (a, repr (self.canvas.get_property (a)))

	def save_item (item, document, parent):
	    node = itemstorage.save (item, document, parent)

	    if isinstance (item, diacanvas.CanvasGroup):
	        for child in item.children:
		    save_item (child, document, node)

	save_item (self.canvas.root, document, canvas)
	return node

    def load (self, node):
        UML.Namespace.load (self, node)
	self.transtable = { } # table to translate 'cid' to object

	# First create all objects:
	canvasnode = node.firstChild
	while canvasnode and canvasnode.tagName != 'Canvas':
	    canvasnode = canvasnode.nextSibling
	assert canvasnode != None

	# Load canvas properties:
	for a in [ 'extents', 'static_extents', 'snap_to_grid',
		   'grid_int_x', 'grid_int_y', 'grid_ofs_x',
		   'grid_ofs_y', 'snap_to_grid', 'grid_color', 'grid_bg' ]:
	    attr = canvasnode.getAttribute (a)
	    if attr:
		self.canvas.set_property (a, eval (attr))
	    
	rootnode = canvasnode.firstChild
	assert rootnode.tagName == 'CanvasItem'
	assert rootnode.getAttribute ('type') == 'CanvasGroup'
	
	def load_item (item, node):
	    itemstorage.load (item, node)

	    # Create child items in case of a canvas group...
	    if isinstance (item, diacanvas.CanvasGroup):
	        childnode = node.firstChild
		while childnode:
		    if childnode.tagName == 'CanvasItem':
			typestr = childnode.getAttribute ('type')
			type = getattr (diagramitems, typestr)
			childitem = item.add (type)
			load_item (childitem, childnode)
		    childnode = childnode.nextSibling
	
	load_item (self.canvas.root, rootnode)
	self.transtable = itemstorage.get_transtable ()
	self.canvas.update_now ()

    def postload (self, node): 
        '''We use postload() to connect objects to each other. This can not
	be done in the load() method, since objects can change their size and
	contents after we have connected to them (since they are not yet
	initialized).'''

        itemstorage.set_transtable (self.transtable)

	canvasnode = node.firstChild
	while canvasnode and canvasnode.tagName != 'Canvas':
	    canvasnode = canvasnode.nextSibling
	assert canvasnode != None
	
	rootnode = canvasnode.firstChild
	assert rootnode.tagName == 'CanvasItem'
	assert rootnode.getAttribute ('type') == 'CanvasGroup'
	
	def postload_item (item, node):
	    itemstorage.postload (item, node)

	    # Do examine child objects:
	    if isinstance (item, diacanvas.CanvasGroup):
	        childnode = node.firstChild
		childindex = 0
		children = item.children
		while childnode:
		    if childnode.tagName == 'CanvasItem':
			postload_item (children[childindex], childnode)
			childindex += 1
		    childnode = childnode.nextSibling
	    
	postload_item (self.canvas.root, rootnode)
	del self.transtable
	itemstorage.flush_transtable ()
