# vim: sw=4
"""
This module contains a model element Diagram which is the abstract
representation of a UML diagram. Diagrams can be visualized and edited.
"""

__author__ = 'Arjan Molenaar'
__version__ = '$revision$'
__date__ = '$date$'

from zope import component
import gobject
import gaphas
from gaphor.misc import uniqueid
from uml2 import Namespace, PackageableElement
from event import DiagramItemCreateEvent

class DiagramCanvas(gaphas.Canvas):
    """
    Some additions to gaphas.Canvas class.
    Esp. load and save functionallity.
    """

    def __init__(self, diagram):
        super(DiagramCanvas, self).__init__()
        self._diagram = diagram
        self._block_updates = False

    diagram = property(lambda s: s._diagram)

    def _set_block_updates(self, block):
        self._block_updates = block
        if not block:
            self.update_now()

    block_updates = property(lambda s: s._block_updates, _set_block_updates)

    def update_now(self):
        if self._block_updates:
            #log.debug('Update blocked for canvas %s' % self)
            return
        super(DiagramCanvas, self).update_now()

    def save(self, save_func):
        #for prop in DiagramCanvas._savable_canvas_properties:
        #    save_func(prop, self.get_property(prop))
        #save_func('root_affine', self.root.get_property('affine'))
        # Save child items:
        for item in self.get_root_items():
            save_func(None, item)

    def postload(self):
        pass #self.block_updates = False

    def select(self, expression=lambda e: True):
        """
        Return a list of all canvas items that match expression.
        """
        return filter(expression, self.get_all_items())


class Diagram(Namespace, PackageableElement):
    """
    Diagrams may contain model elements and can be owned by a Package.
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

    def create(self, type, parent=None, subject=None):
        """
        Create a new canvas item on the canvas. It is created with
        a unique ID and it is attached to the diagram's root item.
        """
        assert issubclass(type, gaphas.Item)
        obj = type(uniqueid.generate_id())
        if subject:
            obj.subject = subject
        self.canvas.add(obj, parent)
        print 'send event', obj
        component.handle(DiagramItemCreateEvent(obj))
        return obj

    def unlink(self):
        # Make sure all canvas items are unlinked
        for item in self.canvas.get_all_items():
            try:
                item.unlink()
            except:
                pass

        super(Diagram, self).unlink()
