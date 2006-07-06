# vim: sw=4
'''diagram.py
This module contains a model elements (!) Diagram which is the abstract
representation of a UML diagram. Diagrams can be visualized and edited.'''

__author__ = 'Arjan Molenaar'
__version__ = '$revision$'
__date__ = '$date$'

import gobject
import gaphas
from gaphor.misc import uniqueid
from uml2 import Namespace, PackageableElement

class DiagramCanvas(gaphas.Canvas):
    """Some additions to gaphas.Canvas class.
    Esp. load and save functionallity.
    """
    # TODO: save or ignore properties coming from diacanvas.Canvas
    #_savable_canvas_properties = [ 'extents', 'static_extents',
    #        'snap_to_grid', 'grid_int_x', 'grid_int_y', 'grid_ofs_x',
    #        'grid_ofs_y', 'grid_color', 'grid_bg' ]

    def __init__(self, diagram):
        super(DiagramCanvas, self).__init__()
        self._diagram = diagram

    diagram = property(lambda d: d._diagram)

    def save(self, save_func):
        #for prop in DiagramCanvas._savable_canvas_properties:
        #    save_func(prop, self.get_property(prop))
        #save_func('root_affine', self.root.get_property('affine'))
        # Save child items:
        for item in self.get_root_items():
            save_func(None, item)

    def postload(self):
        self.update_now()

    def select(self, expression=lambda e: True):
        """Return a list of all canvas items that match expression.
        """
        return filter(expression, self.get_all_items())


class Diagram(Namespace, PackageableElement):
    """Diagrams may contain model elements and can be owned by a Package.
    """

    def __init__(self, id=None, factory=None):
        super(Diagram, self).__init__(id, factory)
        self.canvas = DiagramCanvas(self)

    def save(self, save_func):
        super(Diagram, self).save(save_func)
        save_func('canvas', self.canvas)

    def postload(self):
        super(Diagram, self).postload()
        self.canvas.postload()

    def create(self, type, parent=None):
        """Create a new canvas item on the canvas. It is created with
        a unique ID and it is attached to the diagram's root item.
        """
        assert issubclass(type, gaphas.Item)
        obj = type(uniqueid.generate_id())
        self.canvas.add(obj, parent)
        return obj

    def unlink(self):
        # Make sure all canvas items are unlinked
        for item in self.canvas.all_items():
            try:
                item.unlink()
            except:
                pass

        super(Diagram, self).unlink()
