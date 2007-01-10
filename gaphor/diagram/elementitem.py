"""
ElementItem

Abstract base class for element-like Diagram items.
"""

import gobject
import gaphas
from diagramitem import DiagramItem

__version__ = '$Revision$'

class ElementItem(gaphas.Element, DiagramItem):
    __style__ = {
        'min-size': (0, 0),
    }

    def __init__(self, id=None):
        gaphas.Element.__init__(self)
        DiagramItem.__init__(self, id)

        self.min_width   = self.style.min_size[0]
        self.min_height  = self.style.min_size[1]
        self.auto_resize = 0

    def save(self, save_func):
        save_func('matrix', tuple(self.matrix))
        for prop in ('width', 'height'):
            self.save_property(save_func, prop)
        DiagramItem.save(self, save_func)

    def load(self, name, value):
        if name == 'matrix':
            self.matrix = eval(value)
        else:
            DiagramItem.load(self, name, value)

    def pre_update(self, context):
	super(ElementItem, self).pre_update(context)
	self.update_stereotype()

# vim:sw=4
