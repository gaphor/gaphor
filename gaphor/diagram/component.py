"""
Component item.
"""

import diacanvas
from gaphor import UML
from gaphor.diagram.classifier import ClassifierItem

class ComponentItem(ClassifierItem):

    __uml__  = UML.Component
    __icon__ = True

    BAR_WIDTH     = 10
    BAR_HEIGHT    =  5
    BAR_PADDING   =  5

    popup_menu = ClassifierItem.popup_menu \
        + ('separator', 'IndirectlyInstantiated')

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        # Set drawing style to compartment w// small icon
        self.drawing_style = self.DRAW_COMPARTMENT_ICON

        for attr in ('_component_icon', '_lower_bar', '_upper_bar'):
            shape = diacanvas.shape.Path()
            shape.set_line_width(1.0)
            shape.set_fill(True)
            shape.set_fill_color(diacanvas.color(255, 255, 255))
            setattr(self, attr, shape)

        self._shapes.update((self._component_icon,
            self._lower_bar,
            self._upper_bar))


    def update_compartment_icon(self, affine):
        ClassifierItem.update_compartment_icon(self, affine)

        # draw icon
        ix, iy = self.get_icon_pos()

        self._component_icon.rectangle((ix, iy),
            (ix + self.ICON_WIDTH, iy + self.ICON_HEIGHT))

        bx = ix - self.BAR_PADDING
        bar_upper_y = iy + self.BAR_PADDING
        bar_lower_y = iy + self.BAR_PADDING * 3

        self._lower_bar.rectangle((bx, bar_lower_y),
            (bx + self.BAR_WIDTH, bar_lower_y + self.BAR_HEIGHT))
        self._upper_bar.rectangle((bx, bar_upper_y),
            (bx + self.BAR_WIDTH, bar_upper_y + self.BAR_HEIGHT))

# vim:sw=4:et
