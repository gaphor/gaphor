# vim: sw=4
'''diagram.py
This module contains a model elements (!) Diagram which is the abstract
representation of a UML diagram. Diagrams can be visualized and edited.'''

__author__ = 'Arjan Molenaar'
__version__ = '$revision$'
__date__ = '$date$'

from modelelements import Namespace
from elementfactory import ElementFactory

import diacanvas


class Diagram(Namespace):
    _attrdef = { 'canvas': ( None, diacanvas.Canvas ) }
    # Diagram item to UML model element mapping:
    diagram2UML = { }
    _savable_canvas_properties = [ 'extents', 'static_extents',
	    'snap_to_grid', 'grid_int_x', 'grid_int_y', 'grid_ofs_x',
	    'grid_ofs_y', 'snap_to_grid', 'grid_color', 'grid_bg' ]
    _savable_root_item_properties = [ 'affine', ]
    #__index = 0

    def __init__(self, id):
	Namespace.__init__(self, id)
        self.canvas = diacanvas.Canvas()
	print 'Diagram:', self.canvas
	self.canvas.set_undo_stack_depth(10)
	self.canvas.set_property ("allow_undo", 1)
	print 'Diagram: allow undo =', self.canvas.get_property('allow_undo')

    def save(self, store):
	# Save the diagram attributes, but not the canvas
	self_canvas = self.canvas
	del self.__dict__['canvas']
	node = Namespace.save (self, store)
	self.__dict__['canvas'] = self_canvas
	del self_canvas

	# Save attributes of the canvas:
	canvas_store = store.new (self.canvas)
	for prop in Diagram._savable_canvas_properties:
	    canvas_store.save_property(prop)

	canvas_store.save_attribute ('root_affine', self.canvas.root.get_property('affine'))

	# Save child items:
	for item in self.canvas.root.children:
	    item.save(canvas_store.new(item))

    def load (self, store):
	#print 'Doing Namespace'
        Namespace.load (self, store)
	#print 'Namespace done'

	self.canvas.set_property ("allow_undo", 0)

	# First create the canvas:
	canvas_store = store.canvas()
	for name, value in canvas_store.values().items():
	    print 'Diagram: loading attribute', name
	    if name == 'root_affine':
	    	self.canvas.root.set_property('affine', eval(value))
	    else:
		print 'value = "%s"' % value
		v = eval(value)
		self.canvas.set_property (name, v)

	item_dict = canvas_store.canvas_items()
	
	for id, item_store in item_dict.items():
	    print 'Creating item ' + str(item_store.type()) + ' with id ' + str(id)
	    type = item_store.type()
	    item = type()
	    self.canvas.root.add(item)
	    item_store.add_cid_to_item_mapping (id, item)
	    item.set_property ('id', id)
	    item.load(item_store)

	self.canvas.update_now ()

    def postload (self, store): 
        '''We use postload() to connect objects to each other. This can not
	be done in the load() method, since objects can change their size and
	contents after we have connected to them (since they are not yet
	initialized). We use a transformation table here to retrieve the objects
	and their CID. '''

	# All objects are loaded and the fields are properly set.
	item_dict = store.canvas().canvas_items()
	
	for id, item_store in item_dict.items():
	    print 'Postprocessing item ' + str(item_store.type()) + ' with id ' + str(id)
	    item = store.lookup_item(id)
	    item.postload(item_store)

	self.canvas.update_now ()

	self.canvas.set_property ("allow_undo", 1)

