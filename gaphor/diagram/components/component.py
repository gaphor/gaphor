"""
Component item.
"""

from gaphor import UML
from gaphor.diagram.classifier import ClassifierItem


class ComponentItem(ClassifierItem):

    __uml__ = UML.Component
    __icon__ = True

    __style__ = {"name-padding": (10, 25, 10, 10)}

    BAR_WIDTH = 10
    BAR_HEIGHT = 5
    BAR_PADDING = 5

    def __init__(self, id=None, factory=None):
        ClassifierItem.__init__(self, id, factory)
        # Set drawing style to compartment w// small icon
        self.drawing_style = self.DRAW_COMPARTMENT_ICON

    def draw_compartment_icon(self, context):
        cr = context.cairo
        cr.save()
        self.draw_compartment(context)
        cr.restore()

        ix, iy = self.get_icon_pos()

        cr.set_line_width(1.0)
        cr.rectangle(ix, iy, self.ICON_WIDTH, self.ICON_HEIGHT)
        cr.stroke()

        bx = ix - self.BAR_PADDING
        bar_upper_y = iy + self.BAR_PADDING
        bar_lower_y = iy + self.BAR_PADDING * 3

        color = cr.get_source()
        cr.rectangle(bx, bar_lower_y, self.BAR_WIDTH, self.BAR_HEIGHT)
        cr.set_source_rgb(1, 1, 1)  # white
        cr.fill_preserve()
        cr.set_source(color)
        cr.stroke()

        cr.rectangle(bx, bar_upper_y, self.BAR_WIDTH, self.BAR_HEIGHT)
        cr.set_source_rgb(1, 1, 1)  # white
        cr.fill_preserve()
        cr.set_source(color)
        cr.stroke()


# vim:sw=4:et
