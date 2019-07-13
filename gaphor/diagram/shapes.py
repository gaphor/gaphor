from math import pi, atan2
from gaphas.geometry import Rectangle

from gaphor.diagram.text import (
    text_point_in_box,
    text_size,
    text_draw,
    text_draw_focus_box,
    TextAlign,
    VerticalAlign,
)


def draw_boundry(box, context, bounding_box):
    cr = context.cairo
    d = box.style("border-radius")
    x, y, width, height = bounding_box

    cr.move_to(x, d)
    if d:
        x1 = width + x
        y1 = height + y
        cr.arc(d, d, d, pi, 1.5 * pi)
        cr.line_to(x1 - d, y)
        cr.arc(x1 - d, d, d, 1.5 * pi, y)
        cr.line_to(x1, y1 - d)
        cr.arc(x1 - d, y1 - d, d, 0, 0.5 * pi)
        cr.line_to(d, y1)
        cr.arc(d, y1 - d, d, 0.5 * pi, pi)
    else:
        cr.rectangle(x, y, width, height)

    cr.close_path()
    cr.stroke()


class Box:
    """
    A box like shape.

    CSS properties:
    - min-height
    - min-width
    - padding: a tuple (top, right, bottom, left)

    """

    def __init__(self, *children, style={}, draw=None):
        self.children = children
        self.sizes = []
        self.style = {
            "min-width": 0,
            "min-height": 0,
            "padding": (0, 0, 0, 0),
            **style,
        }.__getitem__
        self._draw_border = draw

    def size(self, cr):
        style = self.style
        min_width = style("min-width")
        min_height = style("min-height")
        padding = style("padding")
        self.sizes = sizes = [c.size(cr) for c in self.children]
        if sizes:
            widths, heights = list(zip(*sizes))
            return (
                max(min_width, max(widths) + padding[1] + padding[3]),
                max(min_height, sum(heights) + padding[0] + padding[2]),
            )
        else:
            return min_width, min_height

    def draw(self, context, bounding_box):
        padding = self.style("padding")
        if self._draw_border:
            self._draw_border(self, context, bounding_box)
        x = bounding_box.x + padding[3]
        y = bounding_box.y + padding[0]
        w = bounding_box.width - padding[1] - padding[3]
        for c, (_w, h) in zip(self.children, self.sizes):
            c.draw(context, Rectangle(x, y, w, h))
            y += h


class Text:
    def __init__(self, text=lambda: "", width=lambda: -1, style={}):
        self.text = text if callable(text) else lambda: text
        self.width = width if callable(width) else lambda: width
        self.style = {
            "width": -1,
            "min-width": 30,
            "min-height": 14,
            "font": "sans 10",
            "text-align": TextAlign.CENTER,
            "vertical-align": VerticalAlign.MIDDLE,
            "padding": (0, 0, 0, 0),
            **style,
        }.__getitem__

    def size(self, cr):
        min_w = self.style("min-width")
        min_h = self.style("min-height")
        font = self.style("font")

        w, h = text_size(cr, self.text(), font, self.width())
        return max(min_w, w), max(min_h, h)

    def draw(self, context, bounding_box):
        cr = context.cairo
        min_w = self.style("min-width")
        min_h = self.style("min-height")
        font = self.style("font")
        text_align = self.style("text-align")
        vertical_align = self.style("vertical-align")
        padding = self.style("padding")

        x, y, w, h = text_draw(
            cr,
            self.text(),
            font,
            lambda w, h: text_point_in_box(
                bounding_box, (w, h), text_align, vertical_align, padding
            ),
            width=bounding_box.width,
            default_size=(min_w, min_h),
        )
        return x, y, w, h


class EditableText(Text):
    def draw(self, context, bounding_box):
        x, y, w, h = super().draw(context, bounding_box)
        text_draw_focus_box(context, x, y, w, h)


def draw_default_head(context):
    """
    Default head drawer: move cursor to the first handle.
    """
    context.cairo.move_to(0, 0)


def draw_default_tail(context):
    """
    Default tail drawer: draw line to the last handle.
    """
    context.cairo.line_to(0, 0)


def draw_arrow_tail(context):
    cr = context.cairo
    cr.line_to(0, 0)
    cr.stroke()
    cr.move_to(15, -6)
    cr.line_to(0, 0)
    cr.line_to(15, 6)


class Line:
    """
    A line, rendered based on a list of points (Position objects).

    CSS properties:

    - line-width
    - dash-style: tuple of floats (line, spacing, ...)
    """

    def __init__(
        self,
        *children,
        style={},
        draw_head=draw_default_head,
        draw_tail=draw_default_tail,
    ):
        super().__init__()
        self.children = children
        self.style = {"dash-style": (), "line-width": 2, **style}.__getitem__
        self._draw_head = draw_head
        self._draw_tail = draw_tail

    def draw(self, context, points):
        def draw_line_end(p0, p1, draw):
            x0, y0 = p0
            x1, y1 = p1
            angle = atan2(y1 - y0, x1 - x0)
            cr.save()
            try:
                cr.translate(*p0)
                cr.rotate(angle)
                draw(context)
            finally:
                cr.restore()

        cr = context.cairo
        cr.set_line_width(self.style("line-width"))
        draw_line_end(points[0], points[1], self._draw_head)
        if self.style("dash-style"):
            cr.set_dash(self.style("dash-style"), 0)
        for p in points[1:-1]:
            cr.line_to(*p)
        draw_line_end(points[-1], points[-2], self._draw_tail)
        cr.stroke()

        for c in self.children:
            c.draw(context, points)
