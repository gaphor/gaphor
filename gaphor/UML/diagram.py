# vim: sw=4
'''diagram.py
This module contains a model elements (!) Diagram which is the abstract
representation of a UML diagram. Diagrams can be visualized and edited.'''

__author__ = 'Arjan Molenaar'
__version__ = '$revision$'
__date__ = '$date$'

import gobject
import diacanvas
import gaphor.misc.uniqueid as uniqueid
from gaphor.undomanager import get_undo_manager
from uml2 import Namespace, PackageableElement

class DiagramCanvas(diacanvas.Canvas):
    """Some additions to diacanvas.Canvas class.
    Esp. load and save functionallity.
    """
    # Most of those properties come from diacanvas.Canvas
    _savable_canvas_properties = [ 'extents', 'static_extents',
            'snap_to_grid', 'grid_int_x', 'grid_int_y', 'grid_ofs_x',
            'grid_ofs_y', 'grid_color', 'grid_bg' ]

    def __init__(self, diagram):
        self.__gobject_init__()
        self._diagram = diagram
        self.set_undo_manager(get_undo_manager())

    diagram = property(lambda d: d._diagram)

    def save(self, save_func):
        for prop in DiagramCanvas._savable_canvas_properties:
            save_func(prop, self.get_property(prop))
        save_func('root_affine', self.root.get_property('affine'))
        # Save child items:
        for item in self.root.children:
            save_func(None, item)

    def postload(self):
        self.set_property ("allow_undo", False)
        self.update_now()
        self.resolve_now()
        self.update_now()

        # setting allow-undo to 1 here will cause update info from later
        # created elements to be put on the undo stack.
        #self.clear_undo()
        #self.clear_redo()
        self.set_property ("allow_undo", True)

    def _select(self, item_list, expression=None):
        l = []
        if expression is None:
            expression = lambda e: 1
        CanvasGroupable = diacanvas.CanvasGroupable
        for item in item_list:
            if expression(item):
                l.append(item)
            if isinstance(item, CanvasGroupable):
                l.extend(self._select(item.groupable_iter(), expression))
        return l

    def select(self, expression=None):
        """Return a list of all canvas items that match expression.
        """
        return self._select(self.root.children, expression)

gobject.type_register(DiagramCanvas)


class Diagram(Namespace, PackageableElement):
    """Diagrams may contain model elements and can be owned by a Package.
    """

    def __init__(self, id=None, factory=None):
        super(Diagram, self).__init__(id, factory)
        self.canvas = DiagramCanvas(self)
        #self.canvas.set_undo_stack_depth(10)
        self.canvas.set_property ("allow_undo", 1)

    def save(self, save_func):
        super(Diagram, self).save(save_func)
        save_func('canvas', self.canvas)

    def postload(self):
        super(Diagram, self).postload()
        self.canvas.postload()

    def create(self, type):
        """Create a new canvas item on the canvas. It is created with
        a unique ID and it is attached to the diagram's root item.
        """
        assert issubclass(type, diacanvas.CanvasItem)
        obj = type(uniqueid.generate_id())
        #obj.set_property('parent', self.canvas.root)
        self.canvas.root.add(obj)
        return obj

    def substitute_item(self, item, new_item_type):
        """Create a new item and replace item with the new item.
        """

    def unlink(self):
        self.canvas.set_property('allow_undo', False)
        # Make sure all canvas items are unlinked
        for item in self.canvas.select():
            try:
                item.unlink()
            except:
                pass

        #self.canvas.clear_undo()
        #self.canvas.clear_redo()

        Namespace.unlink(self)
