'''
ComponentItem diagram item
'''
# vim:sw=4:et

from __future__ import generators

import gobject
import pango
import diacanvas
import gaphor.UML as UML
from gaphor.diagram import initialize_item
from nameditem import NamedItem

#class ComponentIcon(diacanvas.CanvasElement):
#    def __init__(self):
#        self._ci = diacanvas.shape.Path()
#        self._ci.rectangle((self.width - 30, 0), (self.width - 10, 15))
#
#    def on_shape_iter(self):
#        for s in diacanvas.CanvasElement.on_shape_iter(self):
#            yield s
#        yield self._ci


class ComponentItem(NamedItem):
    HEAD_MARGIN_X = 10
    HEAD_MARGIN_Y = 10
    ICON_MARGIN_X = 10
    ICON_MARGIN_Y = 10
    ICON_WIDTH    = 15
    ICON_HEIGHT   = 25
    BAR_WIDTH     = 10
    BAR_HEIGHT    =  5
    BAR_PADDING   =  5

    MARGIN_X      = HEAD_MARGIN_X * 2 + ICON_WIDTH + ICON_MARGIN_X + BAR_PADDING
    MARGIN_Y      = HEAD_MARGIN_Y + ICON_HEIGHT

    popup_menu = NamedItem.popup_menu \
        + ('separator', 'IndirectlyInstantiated')

    def __init__(self, id=None):
        NamedItem.__init__(self, id)
        self.set(height=50, width=120)
        self._border = diacanvas.shape.Path()
        self._border.set_line_width(2.0)

        #self._ci = ComponentIcon()

        for attr in ('_component_icon', '_lower_bar', '_upper_bar'):
            shape = diacanvas.shape.Path()
            shape.set_line_width(1.0)
            shape.set_fill(True)
            shape.set_fill_color(diacanvas.color(255, 255, 255))
            setattr(self, attr, shape)


    def on_update(self, affine):
        # Center the text
        w, h = self.get_name_size()
        self.set(min_width=w + ComponentItem.MARGIN_X,
                 min_height=h + ComponentItem.MARGIN_Y)
        self.update_name(x=ComponentItem.HEAD_MARGIN_X,
                         y=ComponentItem.HEAD_MARGIN_Y + ComponentItem.ICON_MARGIN_Y,
                         width=self.width - ComponentItem.ICON_WIDTH - ComponentItem.ICON_MARGIN_X * 2,
                         height=h)

        NamedItem.on_update(self, affine)

        # draw icon
        ix = self.width - self.ICON_MARGIN_X - self.ICON_WIDTH
        iy = self.ICON_MARGIN_Y

        self._component_icon.rectangle((ix, iy),
            (ix + self.ICON_WIDTH, iy + self.ICON_HEIGHT))

        bx = ix - self.BAR_PADDING
        bar_upper_y = iy + self.BAR_PADDING
        bar_lower_y = iy + self.BAR_PADDING * 3

        self._lower_bar.rectangle((bx, bar_lower_y),
            (bx + self.BAR_WIDTH, bar_lower_y + self.BAR_HEIGHT))
        self._upper_bar.rectangle((bx, bar_upper_y),
            (bx + self.BAR_WIDTH, bar_upper_y + self.BAR_HEIGHT))

        # draw border
        self._border.rectangle((0, 0), (self.width, self.height))
        self.expand_bounds(1.0)

    def on_shape_iter(self):
        yield self._border
        for s in NamedItem.on_shape_iter(self):
            yield s
        yield self._component_icon
        yield self._lower_bar
        yield self._upper_bar

initialize_item(ComponentItem, UML.Component)
