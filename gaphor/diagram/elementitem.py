"""
Abstract classes for element-like Diagram items.
"""

import gobject
import gaphas
from zope import component
from gaphor.application import Application
from gaphor.UML.event import ElementDeleteEvent
from diagramitem import DiagramItem
from gaphor.diagram.style import get_text_point

__version__ = '$Revision$'

class ElementItem(gaphas.Element, DiagramItem):
    __style__ = {
        'min-size': (0, 0),
        'stereotype-padding': (5, 10, 5, 10),
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


    def setup_canvas(self):
        gaphas.Element.setup_canvas(self)
        self.register_handlers()


    def teardown_canvas(self):
        gaphas.Element.teardown_canvas(self)
        self.unregister_handlers()


    def register_handlers(self):
	super(ElementItem, self).register_handlers()
	Application.register_handler(self._on_element_delete)


    def unregister_handlers(self):
	super(ElementItem, self).unregister_handlers()
	Application.unregister_handler(self._on_element_delete)


    @component.adapter(ElementDeleteEvent)
    def _on_element_delete(self, event):
	"""
	Delete the item if the subject is deleted.
	"""
	if event and event.element is self.subject:
	    self.unlink()


    def pre_update(self, context):
        #super(ElementItem, self).pre_update(context)
        self.update_stereotype()
        DiagramItem.pre_update(self, context)
        gaphas.Element.pre_update(self, context)


    def point(self, pos):
        d1 = gaphas.Element.point(self, pos)
        d2 = DiagramItem.point(self, pos)
        return min(d1, d2)


    def post_update(self, context):
        gaphas.Element.post_update(self, context)
        DiagramItem.post_update(self, context)


    def draw(self, context):
        gaphas.Element.draw(self, context)
        DiagramItem.draw(self, context)


    def text_align(self, extents, align, padding, outside):
        x, y = get_text_point(extents, self.width, self.height,
                align, padding, outside)

        return x, y


# vim:sw=4
