# vim: sw=4
"""This module contains a model element Diagram which is the abstract
representation of a UML diagram. Diagrams can be visualized and edited.

The DiagramCanvas class extends the gaphas.Canvas class."""

from __future__ import absolute_import

import uuid

import gaphas
from six.moves import filter

from gaphor.UML.uml2 import Namespace, PackageableElement


class DiagramCanvas(gaphas.Canvas):
    """DiagramCanvas extends the gaphas.Canvas class.  Updates to the canvas
    can be blocked by setting the block_updates property to true.  A save
    function can be applied to all root canvas items.  Canvas items can be
    selected with an optional expression filter."""

    def __init__(self, diagram):
        """Initialize the diagram canvas with the supplied diagram.  By default,
        updates are not blocked."""

        super(DiagramCanvas, self).__init__()
        self._diagram = diagram
        self._block_updates = False

    diagram = property(lambda s: s._diagram)

    def _set_block_updates(self, block):
        """Sets the block_updates property.  If false, the diagram canvas is
        updated immediately."""

        self._block_updates = block
        if not block:
            self.update_now()

    block_updates = property(lambda s: s._block_updates, _set_block_updates)

    def update_now(self):
        """Update the diagram canvas, unless block_updates is true."""

        if self._block_updates:
            return
        super(DiagramCanvas, self).update_now()

    def save(self, save_func):
        """Apply the supplied save function to all root diagram items."""

        for item in self.get_root_items():
            save_func(None, item)

    def postload(self):
        """Called after the diagram canvas has loaded.  Currently does nothing.
        """
        pass

    def select(self, expression=lambda e: True):
        """Return a list of all canvas items that match expression."""

        return list(filter(expression, self.get_all_items()))


class Diagram(Namespace, PackageableElement):
    """Diagrams may contain model elements and can be owned by a Package.
    A diagram is a Namespace and a PackageableElement."""

    def __init__(self, id=None, factory=None):
        """Initialize the diagram with an optional id and element factory.
        The diagram also has a canvas."""

        super(Diagram, self).__init__(id, factory)
        self.canvas = DiagramCanvas(self)

    def save(self, save_func):
        """Apply the supplied save function to this diagram and the canvas."""

        super(Diagram, self).save(save_func)
        save_func('canvas', self.canvas)

    def postload(self):
        """Handle post-load functionality for the diagram canvas."""
        super(Diagram, self).postload()
        self.canvas.postload()

    def create(self, type, parent=None, subject=None):
        """Create a new canvas item on the canvas. It is created with
        a unique ID and it is attached to the diagram's root item.  The type
        parameter is the element class to create.  The new element also has an
        optional parent and subject."""

        assert issubclass(type, gaphas.Item)
        obj = type(str(uuid.uuid1()))
        if subject:
            obj.subject = subject
        self.canvas.add(obj, parent)
        return obj

    def unlink(self):
        """Unlink all canvas items then unlink this diagram."""

        for item in self.canvas.get_all_items():
            try:
                item.unlink()
            except:
                pass

        super(Diagram, self).unlink()
