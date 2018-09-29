"""
Abstract classes for element-like Diagram items.
"""

import cairo
import gaphas

from gaphor.diagram.diagramitem import DiagramItem
from gaphor.diagram.style import get_text_point


class ElementItem(gaphas.Element, DiagramItem):
    __style__ = {
        'min-size': (0, 0),
        'stereotype-padding': (5, 10, 5, 10),
	'background': 'solid',
	'background-color': (1, 1, 1, 0.8),
	'highlight-color': (0, 0, 1, 0.4),
	'background-gradient': ((0.8, 0.8, 0.8, 0.5), (1.0, 1.0, 1.0, 0.5))
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


    def fill_background(self, context):
	cr = context.cairo
	cr.save()
	try:
	    if self.style.background == 'solid':
		cr.set_source_rgba(*self.style.background_color)
		cr.fill_preserve()
		
	    elif self.style.background == 'gradient':
		# TODO: check if style is gradient
		g = cairo.LinearGradient(0, 0, self.width, self.height)
		for i, c in enumerate(self.style.background_gradient):
		    g.add_color_stop_rgba(i, *c)
		cr.set_source(g)
		cr.fill_preserve()
	finally:
	    cr.restore()

    def highlight(self, context):
	cr = context.cairo
	cr.save()
	try:
	    if context.dropzone:
		cr.set_source_rgba(*self.style.highlight_color)
		cr.set_line_width(cr.get_line_width() * 3.141)
		cr.stroke_preserve()
	finally:
	    cr.restore()

    def draw(self, context):
	self.fill_background(context)
        self.highlight(context)
        gaphas.Element.draw(self, context)
        DiagramItem.draw(self, context)


    def text_align(self, extents, align, padding, outside):
        x, y = get_text_point(extents, self.width, self.height,
                align, padding, outside)

        return x, y


# vim:sw=4:et:ai
