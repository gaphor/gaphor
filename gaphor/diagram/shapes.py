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


class Padding:  # Enum
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3


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


def draw_highlight(context):
    highlight_color = (0, 0, 1, 0.4)
    cr = context.cairo
    cr.save()
    try:
        if context.dropzone:
            cr.set_source_rgba(*highlight_color)
            cr.set_line_width(cr.get_line_width() * 3.141)
            cr.stroke_preserve()
    finally:
        cr.restore()


class Box:
    """
    A box like shape.

    Style properties:
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
            "vertical-align": VerticalAlign.MIDDLE,
            "border-radius": 0,
            **style,
        }.__getitem__
        self._draw_border = draw

    def size(self, cr):
        global Padding
        style = self.style
        min_width = style("min-width")
        min_height = style("min-height")
        padding = style("padding")
        self.sizes = sizes = [c.size(cr) for c in self.children]
        if sizes:
            widths, heights = list(zip(*sizes))
            return (
                max(
                    min_width,
                    max(widths) + padding[Padding.RIGHT] + padding[Padding.LEFT],
                ),
                max(
                    min_height,
                    sum(heights) + padding[Padding.TOP] + padding[Padding.BOTTOM],
                ),
            )
        else:
            return min_width, min_height

    def draw(self, context, bounding_box):
        global Padding
        padding = self.style("padding")
        valign = self.style("vertical-align")
        height = sum(h for _w, h in self.sizes)
        if self._draw_border:
            self._draw_border(self, context, bounding_box)
        x = bounding_box.x + padding[Padding.LEFT]
        if valign is VerticalAlign.MIDDLE:
            y = bounding_box.y + (bounding_box.height - height) / 2
        elif valign is VerticalAlign.BOTTOM:
            y = bounding_box.y + bounding_box.height - height - padding[Padding.BOTTOM]
        else:
            y = bounding_box.y + padding[Padding.TOP]
        w = bounding_box.width - padding[Padding.RIGHT] - padding[Padding.LEFT]
        for c, (_w, h) in zip(self.children, self.sizes):
            c.draw(context, Rectangle(x, y, w, h))
            y += h


class IconBox:
    """
    A special type of box: the icon element is given the full width/height and
    all other shapes are drawn below the main icon shape.

    Style properties:
    - min-height
    - min-width
    - vertical-spacing: spacing between icon and children
    - padding: a tuple (top, right, bottom, left)
    """

    def __init__(self, icon, *children, style={}):
        self.icon = icon
        self.children = children
        self.sizes = []
        self.style = {
            "min-width": 0,
            "min-height": 0,
            "vertical-spacing": 4,
            "padding": (0, 0, 0, 0),
            **style,
        }.__getitem__

    def size(self, cr):
        global Padding
        style = self.style
        min_width = style("min-width")
        min_height = style("min-height")
        padding = style("padding")
        self.sizes = [c.size(cr) for c in self.children]
        width, height = self.icon.size(cr)
        return (
            max(min_width, width + padding[Padding.RIGHT] + padding[Padding.LEFT]),
            max(min_height, height + padding[Padding.TOP] + padding[Padding.BOTTOM]),
        )

    def draw(self, context, bounding_box):
        global Padding
        padding = self.style("padding")
        vertical_spacing = self.style("vertical-spacing")
        x = bounding_box.x + padding[Padding.LEFT]
        y = bounding_box.y + padding[Padding.TOP]
        w = bounding_box.width - padding[Padding.RIGHT] - padding[Padding.LEFT]
        h = bounding_box.height - padding[Padding.TOP] - padding[Padding.BOTTOM]
        self.icon.draw(context, Rectangle(x, y, w, h))
        y = y + bounding_box.height + vertical_spacing
        for c, (cw, ch) in zip(self.children, self.sizes):
            mw = max(w, cw)
            c.draw(context, Rectangle(x - (mw - w) / 2, y, mw, ch))
            y += ch


class Text:
    def __init__(self, text=lambda: "", width=lambda: -1, style={}):
        self._text = text if callable(text) else lambda: text
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

    def text(self):
        try:
            return self._text()
        except AttributeError:
            return ""

    def size(self, cr):
        min_w = self.style("min-width")
        min_h = self.style("min-height")
        font = self.style("font")

        w, h = text_size(cr, self.text(), font, self.width())
        return max(min_w, w), max(min_h, h)

    def draw(self, context, bounding_box):
        cr = context.cairo
        min_w = max(self.style("min-width"), bounding_box.width)
        min_h = max(self.style("min-height"), bounding_box.height)
        font = self.style("font")
        text_align = self.style("text-align")
        vertical_align = self.style("vertical-align")
        padding = self.style("padding")

        x, y, w, h = text_draw(
            cr,
            self.text(),
            font,
            lambda w, h: text_point_in_box(
                bounding_box, (w, h), text_align, vertical_align
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


def draw_arrow_head(context):
    cr = context.cairo
    cr.set_dash((), 0)
    cr.move_to(15, -6)
    cr.line_to(0, 0)
    cr.line_to(15, 6)
    cr.stroke()
    cr.move_to(0, 0)


def draw_arrow_tail(context):
    cr = context.cairo
    cr.line_to(0, 0)
    cr.stroke()
    cr.move_to(15, -6)
    cr.line_to(0, 0)
    cr.line_to(15, 6)
