'''
ComponentItem diagram item
'''
# vim:sw=4:et

from __future__ import generators

import gobject
import pango
import diacanvas
from gaphor import UML
from classifier import ClassifierItem

class ComponentItem(ClassifierItem):

    __uml__ = UML.Component

    BAR_WIDTH     = 10
    BAR_HEIGHT    =  5
    BAR_PADDING   =  5

    popup_menu = ClassifierItem.popup_menu \
        + ('separator', 'IndirectlyInstantiated')

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        self.set(height=50, width=120)
        # Set drawing style to compartment w// small icon
        self.drawing_style = self.DRAW_COMPARTMENT_ICON

        for attr in ('_component_icon', '_lower_bar', '_upper_bar'):
            shape = diacanvas.shape.Path()
            shape.set_line_width(1.0)
            shape.set_fill(True)
            shape.set_fill_color(diacanvas.color(255, 255, 255))
            setattr(self, attr, shape)

    def update_compartment_icon(self, affine):

        ClassifierItem.update_compartment_icon(self, affine)

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

    def on_shape_iter(self):
        for s in ClassifierItem.on_shape_iter(self):
            yield s
        yield self._component_icon
        yield self._lower_bar
        yield self._upper_bar
