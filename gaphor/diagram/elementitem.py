"""
ElementItem

Abstract base class for element-like Diagram items.
"""

import gobject
import gaphas
from diagramitem import DiagramItem

__version__ = '$Revision$'

class ElementItem(gaphas.Element, DiagramItem):
    def __init__(self, id=None):
        gaphas.Element.__init__(self)
        DiagramItem.__init__(self, id)
        self.auto_resize = 0

    def save(self, save_func):
        for prop in ('affine', 'width', 'height', 'auto-resize'):
            self.save_property(save_func, prop)
        DiagramItem.save(self, save_func)

    def load(self, name, value):
        DiagramItem.load(self, name, value)


# vim:sw=4
