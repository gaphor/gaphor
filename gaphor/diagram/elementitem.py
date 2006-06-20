"""
ElementItem

Abstract base class for element-like Diagram items.
"""

import gobject
import gaphas
from diagramitem import DiagramItem
from gaphor.diagram import DiagramItemMeta

__revision__ = '$revision$'
__author__ = 'Arjan J. Molenaar'
__date__ = '$date$'


class ElementItem(gaphas.Element, DiagramItem):
    __metaclass__ = DiagramItemMeta

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

    # DiaCanvasItem callbacks:

    def on_glue(self, handle, wx, wy):
        #import sys
        #print self, handle, '=>', sys.getrefcount(self), sys.getrefcount(handle)
        return self._on_glue(handle, wx, wy, diacanvas.CanvasElement)

    def on_connect_handle(self, handle):
        return self._on_connect_handle(handle, diacanvas.CanvasElement)

    def on_disconnect_handle(self, handle):
        return self._on_disconnect_handle(handle, diacanvas.CanvasElement)

# vim:sw=4
