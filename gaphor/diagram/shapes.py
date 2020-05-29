from math import pi
from typing import List, Optional, Tuple

from gaphas.canvas import Context
from gaphas.geometry import Rectangle
from typing_extensions import TypedDict

from gaphor.diagram.text import (
    FontStyle,
    FontWeight,
    TextAlign,
    TextDecoration,
    VerticalAlign,
    focus_box_pos,
    text_draw,
    text_draw_focus_box,
    text_size,
)

Style = TypedDict(
    "Style",
    {
        "padding": Tuple[float, float, float, float],
        "min-width": float,
        "min-height": float,
        "line-width": float,
        "vertical-spacing": float,
        "border-radius": float,
        "fill": str,
        "font-family": str,
        "font-size": float,
        "font-style": FontStyle,
        "font-weight": Optional[FontWeight],
        "text-decoration": Optional[TextDecoration],
        "text-align": TextAlign,
        "stoke": str,
        "vertical-align": VerticalAlign,
        # CommentItem:
        "ear": int,
    },
    total=False,
)


class Padding:  # Enum
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3


def draw_border(box, context, bounding_box):
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

    fill = box.style("fill")
    if fill:
        color = cr.get_source()
        cr.set_source_rgb(1, 1, 1)  # white
        cr.fill_preserve()
        cr.set_source(color)

    draw_highlight(context)

    cr.stroke()


def draw_top_separator(box, context, bounding_box):
    x, y, w, h = bounding_box
    cr = context.cairo
    cr.move_to(x, y)
    cr.line_to(x + w, y)
    cr.stroke()


def draw_highlight(context):
    if not context.dropzone:
        return
    highlight_color = (0, 0, 1, 0.4)
    cr = context.cairo
    cr.save()
    try:
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
    - vertical-align: alignment of child shapes
    - border-radius
    """

    def __init__(self, *children, style: Style = {}, draw=None):
        self.children = children
        self.sizes: List[Tuple[int, int]] = []
        self._style: Style = {
            "min-width": 0,
            "min-height": 0,
            "padding": (0, 0, 0, 0),
            "vertical-align": VerticalAlign.MIDDLE,
            "border-radius": 0,
            "fill": None,
            **style,  # type: ignore[misc] # noqa: F821
        }
        self._draw_border = draw

    @property
    def style(self):
        return self._style.__getitem__

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, index):
        return self.children[index]

    def size(self, cr):
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
        padding = self.style("padding")
        valign = self.style("vertical-align")
        height = sum(h for _w, h in self.sizes)
        if self._draw_border:
            self._draw_border(self, context, bounding_box)
        x = bounding_box.x + padding[Padding.LEFT]
        if valign is VerticalAlign.MIDDLE:
            y = (
                bounding_box.y
                + padding[Padding.TOP]
                + (max(height, bounding_box.height - padding[Padding.TOP]) - height) / 2
            )
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

    def __init__(self, icon, *children, style: Style = {}):
        self.icon = icon
        self.children = children
        self.sizes: List[Tuple[int, int]] = []
        self._style: Style = {
            "min-width": 0,
            "min-height": 0,
            "vertical-spacing": 4,
            "padding": (0, 0, 0, 0),
            **style,  # type: ignore[misc] # noqa: F821
        }

    @property
    def style(self):
        return self._style.__getitem__

    def size(self, cr):
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
    def __init__(self, text=lambda: "", width=lambda: -1, style: Style = {}):
        self._text = text if callable(text) else lambda: text
        self.width = width if callable(width) else lambda: width
        self._style: Style = {
            "min-width": 30,
            "min-height": 14,
            "font-family": "sans",
            "font-size": 14,
            "font-style": FontStyle.NORMAL,
            "font-weight": None,
            "text-decoration": None,
            "text-align": TextAlign.CENTER,
            "vertical-align": VerticalAlign.MIDDLE,
            "padding": (0, 0, 0, 0),
            **style,  # type: ignore[misc] # noqa: F821
        }

    @property
    def style(self):
        return self._style.__getitem__

    def text(self):
        try:
            return self._text()
        except AttributeError:
            return ""

    def font(self):
        style = self.style
        return {
            "font-family": style("font-family"),
            "font-size": style("font-size"),
            "font-style": style("font-style"),
            "font-weight": style("font-weight"),
            "text-decoration": style("text-decoration"),
        }

    def size(self, cr):
        min_w = self.style("min-width")
        min_h = self.style("min-height")
        padding = self.style("padding")

        width, height = text_size(cr, self.text(), self.font(), self.width())
        return (
            max(min_w, width + padding[Padding.RIGHT] + padding[Padding.LEFT]),
            max(min_h, height + padding[Padding.TOP] + padding[Padding.BOTTOM]),
        )

    def text_box(self, bounding_box: Rectangle) -> Rectangle:
        """Add padding to a bounding box."""
        padding = self.style("padding")
        return Rectangle(
            bounding_box.x + padding[Padding.LEFT],
            bounding_box.y + padding[Padding.TOP],
            bounding_box.width - padding[Padding.RIGHT] - padding[Padding.LEFT],
            bounding_box.height - padding[Padding.TOP] - padding[Padding.BOTTOM],
        )

    def draw(
        self, context: Context, bounding_box: Rectangle
    ) -> Tuple[int, int, int, int]:
        """Draw the text, return the location and size."""
        cr = context.cairo
        min_w = max(self.style("min-width"), bounding_box.width)
        min_h = max(self.style("min-height"), bounding_box.height)
        text_align = self.style("text-align")
        text_box = self.text_box(bounding_box)

        x, y, w, h = text_draw(
            cr,
            self.text(),
            self.font(),
            lambda w, h: (bounding_box.x, bounding_box.y),
            width=text_box.width,
            default_size=(min_w, min_h),
            text_align=text_align,
        )
        return x, y, w, h


class EditableText(Text):
    def __init__(self, text=lambda: "", width=lambda: -1, style: Style = {}):
        super().__init__(text, width, style)
        self.bounding_box = Rectangle()
        self.text_size = (0, 0)

    def size(self, cr):
        s = super().size(cr)
        self.text_size = s
        return s

    def draw(
        self, context: Context, bounding_box: Rectangle
    ) -> Tuple[int, int, int, int]:
        """Draw the editable text."""
        x, y, w, h = super().draw(context, bounding_box)
        text_box = self.text_box(bounding_box)
        text_align = self.style("text-align")
        vertical_align = self.style("vertical-align")
        x, y = focus_box_pos(text_box, self.text_size, text_align, vertical_align)
        text_draw_focus_box(context, x, y, w, h)
        self.bounding_box = Rectangle(x, y, width=w, height=h)
        return x, y, w, h


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
