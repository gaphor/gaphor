"""
Action diagram item.
"""

from math import pi

from gaphor import UML
from gaphor.UML.presentation import ElementPresentation
from gaphor.diagram.support import set_diagram_item
from gaphor.diagram.text import Name
from gaphor.diagram.support import represents


class Box:
    def __init__(self, *children, style={}, draw=None):
        self.children = children
        self.style = {
            "min-width": 0,
            "min-height": 0,
            "padding": (0, 0, 0, 0),
            **style,
        }.__getitem__
        self._draw = draw

    def size(self, cr):
        style = self.style
        min_width = style("min-width")
        min_height = style("min-height")
        padding = style("padding")
        widths, heights = list(zip(*[c.size(cr) for c in self.children]))
        return (
            max(min_width, max(widths) + padding[1] + padding[3]),
            max(min_height, sum(heights) + padding[0] + padding[2]),
        )

    def draw(self, cr, bounding_box):
        if self._draw:
            self._draw(self, cr, bounding_box)
        for c in self.children:
            c.draw(cr, bounding_box)


@represents(UML.Action)
class ActionItem(ElementPresentation):
    def __init__(self, id=None, model=None):
        """
        Create action item.
        """
        super().__init__(id, model)

        self.layout = Box(
            Name(self),
            style={
                "min-width": 50,
                "min-height": 30,
                "padding": (5, 10, 5, 10),
                "border-radius": 15,
            },
            draw=self.draw_border,
        )

    def draw_border(self, box, cr, bounding_box):
        d = box.style("border-radius")
        x, y, width, height = bounding_box
        width += x
        height += y

        cr.move_to(x, d)
        cr.arc(d, d, d, pi, 1.5 * pi)
        cr.line_to(width - d, y)
        cr.arc(width - d, d, d, 1.5 * pi, y)
        cr.line_to(width, height - d)
        cr.arc(width - d, height - d, d, 0, 0.5 * pi)
        cr.line_to(d, height)
        cr.arc(d, height - d, d, 0.5 * pi, pi)
        cr.close_path()
        cr.stroke()


@represents(UML.SendSignalAction)
class SendSignalActionItem(ElementPresentation):
    def __init__(self, id=None, model=None):
        """
        Create action item.
        """
        super().__init__(id, model)

        self.layout = Box(
            Name(self),
            style={"min-width": 50, "min-height": 30, "padding": (5, 25, 5, 10)},
            draw=self.draw_border,
        )

    def draw_border(self, box, cr, bounding_box):
        d = 15
        x, y, width, height = bounding_box
        cr.move_to(0, 0)
        cr.line_to(width - d, 0)
        cr.line_to(width, height / 2)
        cr.line_to(width - d, height)
        cr.line_to(0, height)
        cr.close_path()

        cr.stroke()


@represents(UML.AcceptEventAction)
class AcceptEventActionItem(ElementPresentation):
    def __init__(self, id=None, model=None):
        """
        Create action item.
        """
        super().__init__(id, model)

        self.layout = Box(
            Name(self),
            style={"min-width": 50, "min-height": 30, "padding": (5, 10, 5, 25)},
            draw=self.draw_border,
        )

    def draw_border(self, box, cr, bounding_box):
        d = 15
        x, y, width, height = bounding_box
        cr.move_to(0, 0)
        cr.line_to(width, 0)
        cr.line_to(width, height)
        cr.line_to(0, height)
        cr.line_to(d, height / 2)
        cr.close_path()

        cr.stroke()
