# vim: sw=4
'''diagram.py
This module contains a model elements (!) Diagram which is the abstract
representation of a UML diagram. Diagrams can be visualized and edited.'''

__author__ = 'Arjan Molenaar'
__version__ = '$revision$'
__date__ = '$date$'

from modelelements import * #Namespace, Name, VisibilityKind, VK_PUBLIC, Boolean, Dependency, Constraint, Flow, Comment, TemplateParameter, Stereotype, TaggedValue, Generalization, ModelElement
#import gobject
import diacanvas
import gaphor.misc.uniqueid as uniqueid

class _Canvas(diacanvas.Canvas):
    '''
    Some additions to diacanvas.Canvas class, esp. load and save functionallity.
    '''
    _savable_canvas_properties = [ 'extents', 'static_extents',
	    'snap_to_grid', 'grid_int_x', 'grid_int_y', 'grid_ofs_x',
	    'grid_ofs_y', 'grid_color', 'grid_bg' ]

    def save(self, save_func):
	for prop in _Canvas._savable_canvas_properties:
	    save_func(prop, self.get_property(prop))
	save_func('root_affine', self.root.get_property('affine'))
	# Save child items:
	for item in self.root.children:
	    save_func(None, item) #item.save(canvas_store.new(item))

    def load(self, name, value):
	self.set_property ("allow_undo", 0)

	# First create the canvas:
	if name == 'root_affine':
	    self.root.set_property('affine', eval(value))
	else:
	    self.set_property (name, eval(value))

	self.update_now ()

    def postload(self):
	self.update_now ()

	# setting allow-undo to 1 here will cause update info from later
	# created elements to be put on the undo stack.
	self.clear_undo()
	self.clear_redo()
	self.set_property ("allow_undo", 1)

#gobject.type_register(_Canvas)


class Diagram(Namespace):
    __abstract__ = False
    __attributes__ = {
        # from ModelElement:
	'name': ( '', Name ),
	'visibility': ( VK_PUBLIC, VisibilityKind ),
	'isSpecification': ( False, Boolean ),
	'namespace': ( None, Namespace, 'ownedElement' ),
	'clientDependency': ( Sequence, Dependency, 'client' ),
	'constraint': ( Sequence, Constraint, 'constrainedElement' ),
	'targetFlow': ( Sequence, Flow, 'target' ),
	'sourceFlow': ( Sequence, Flow, 'source' ),
	'comment': ( Sequence, Comment, 'annotatedElement' ),
	'templateParameter': ( Sequence, TemplateParameter, 'template' ),
	'stereotype': ( Sequence, Stereotype ),
	'taggedValue': ( Sequence, TaggedValue, 'modelElement' ),
	# from GeneralizableElement:
	'isRoot': ( False, Boolean ),
	'isLeaf': ( False, Boolean ),
	'isAbstract': ( False, Boolean ),
	'generalization': ( Sequence, Generalization, 'child' ),
	# from Namespace:
	'ownedElement': ( Sequence, ModelElement, 'namespace' ),
	# from Diagram:
	'canvas': ( None, diacanvas.Canvas )
    }

    def __init__(self, id):
	Namespace.__init__(self, id)
        self.canvas = _Canvas()
	self.canvas.set_undo_stack_depth(10)
	self.canvas.set_property ("allow_undo", 1)

    def create(self, type):
	"""
	Create a new canvas item on the canvas. It is created with a unique
	ID and it is attached to the diagram's root item.
	"""
	assert issubclass(type, diacanvas.CanvasItem)
	obj = type()
	obj.set_property('id', uniqueid.generate_id())
	obj.set_property('parent', self.canvas.root)
	return obj

