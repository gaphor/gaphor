# vim: sw=4
'''diagram.py
This module contains a model elements (!) Diagram which is the abstract
repreesentation of a UML diagram.'''

import UML, diacanvas, types
from diagram import *
#from usecase import UseCaseItem
#from actor import ActorItem

# We should get rid of the CID, since it changes a lot of values each save
# so it is not really useful for archiving in CVS. Each item should create
# a unique ID and keep it throughout the lifetime of the item. ID's could
# be created on a diagram basis (this makes the diagram the
# CanvasItemFactory).

#_diagram2UML = {
#	ActorItem: UML.Actor,
#	Comment: UML.Comment,
#	UseCaseItem: UML.UseCase
#	CommentLine: None,
#	Generalization: None
#}

class Diagram(UML.Namespace):
    _attrdef = { 'canvas': ( None, diacanvas.Canvas ) }
    _savable_canvas_properties = [ 'extents', 'static_extents',
	    'snap_to_grid', 'grid_int_x', 'grid_int_y', 'grid_ofs_x',
	    'grid_ofs_y', 'snap_to_grid', 'grid_color', 'grid_bg' ]
    _savable_root_item_properties = [ 'affine', ]
    __index = 0

    def __init__(self, id):
	UML.Namespace.__init__(self, id)
        self.canvas = diacanvas.Canvas()
	print 'Diagram:', self.canvas
	self.canvas.set_property ("allow_undo", 1)

    def create (self, type, pos=(0, 0), subject=None):
	item = type()
	self.canvas.root.add(item)
	if not subject:
	    uml_type = None#_diagram2UML[type]
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
	item.set_property ('id', Diagram.__index)
	Diagram.__index += 1
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

	canvas_store.save ('root_affine', self.canvas.root.get_property('affine'))

	# Save child items:
	for item in self.canvas.root.children:
	    item.save(canvas_store.new(item))

    def load (self, store):
	#print 'Doing Namespace'
        UML.Namespace.load (self, store)
	#print 'Namespace done'

	self.canvas.set_property ("allow_undo", 0)

	# First create the canvas:
	canvas_store = store.canvas()
	for name, value in canvas_store.values().items():
	    if name == 'root_affine':
	    	self.canvas.root.set_property('affine', eval(value))
	    else:
		self.canvas.set_property (name, eval(value))

	item_dict = canvas_store.canvas_items()
	
	for id, item_store in item_dict.items():
	    print 'Creating item ' + str(item_store.type()) + ' with id ' + str(id)
	    type = item_store.type()
	    item = type()
	    self.canvas.root.add(item)
	    item.set_property ('id', item_store.cid())
	    item.load(item_store)

    def postload (self, store): 
        '''We use postload() to connect objects to each other. This can not
	be done in the load() method, since objects can change their size and
	contents after we have connected to them (since they are not yet
	initialized). We use a transformation table here to retrieve the objects
	and their CID. '''

	# All objects are loaded and the fields are properly set.
	self.canvas.update_now ()

	self.canvas.set_property ("allow_undo", 1)
