"""
Action diagram item.
"""

from math import pi

from gaphor import UML
from gaphor.UML.presentation import PresentationElement
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_MIDDLE
from gaphor.diagram.support import set_diagram_item
from gaphor.diagram.text import Text


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
            self._draw(cr, bounding_box)
        for c in self.children:
            c.draw(cr, bounding_box)


def represents(uml_element):
    def wrapper(presentation):
        set_diagram_item(uml_element, presentation)
        return presentation

    return wrapper


@represents(UML.Action)
class ActionItem(PresentationElement):
    def __init__(self, id=None, model=None):
        """
        Create named item.
        """
        super().__init__(id, model)

        self._name = Text("name")

        self.layout = Box(
            self._name,
            style={"min-width": 50, "min-height": 30, "padding": (5, 10, 5, 10)},
            draw=self.draw_border,
        )

        self.watch("subject<NamedElement>.name", self.on_named_element_name)

    def on_named_element_name(self, event):
        """
        Callback to be invoked, when named element name is changed.
        """
        if self.subject:
            self._name.text = self.subject.name
            self.request_update()

    def pre_update(self, context):
        cr = context.cairo
        self.min_width, self.min_height = self.layout.size(cr)

    def post_update(self, context):
        pass

    def draw(self, context):
        """
        Draw action symbol.
        """
        cr = context.cairo
        self.layout.draw(cr, (0, 0, self.width, self.height))
        # self.draw_border(cr, (0, 0, self.width, self.height))

    def draw_border(self, cr, bounding_box):
        d = 15
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


class SendSignalActionItem(NamedItem):
    __uml__ = UML.SendSignalAction
    __style__ = {"min-size": (50, 30), "name-align": (ALIGN_CENTER, ALIGN_MIDDLE)}

    def draw(self, context):
        """
        Draw action symbol.
        """
        super(SendSignalActionItem, self).draw(context)

        c = context.cairo

        d = 15
        w = self.width
        h = self.height
        c.move_to(0, 0)
        c.line_to(w - d, 0)
        c.line_to(w, h / 2)
        c.line_to(w - d, h)
        c.line_to(0, h)
        c.close_path()

        c.stroke()


class AcceptEventActionItem(NamedItem):
    __uml__ = UML.SendSignalAction
    __style__ = {"min-size": (50, 30), "name-align": (ALIGN_CENTER, ALIGN_MIDDLE)}

    def draw(self, context):
        """
        Draw action symbol.
        """
        super(AcceptEventActionItem, self).draw(context)

        c = context.cairo

        d = 15
        w = self.width
        h = self.height
        c.move_to(0, 0)
        c.line_to(w, 0)
        c.line_to(w, h)
        c.line_to(0, h)
        c.line_to(d, h / 2)
        c.close_path()

        c.stroke()
