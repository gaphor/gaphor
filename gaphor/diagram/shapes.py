from __future__ import annotations

from dataclasses import dataclass, replace
from math import pi
from typing import Callable, List, Optional, Sequence, Tuple, Union

from cairo import Context as CairoContext
from gaphas.geometry import Rectangle
from typing_extensions import TypedDict

from gaphor.diagram.style import Style, combined_style
from gaphor.diagram.text import (
    FontStyle,
    FontWeight,
    TextAlign,
    TextDecoration,
    VerticalAlign,
    focus_box_pos,
    text_draw,
    text_size,
)


@dataclass(frozen=True)
class SizeContext:
    @classmethod
    def from_context(cls, context, style) -> SizeContext:
        return SizeContext(cairo=context.cairo, style=style)

    cairo: CairoContext
    style: Style


@dataclass(frozen=True)
class DrawContext:
    """
    Special context for draw()'ing the item. The draw-context contains
    stuff like the cairo context and flags like selected and
    focused.
    """

    @classmethod
    def from_context(cls, context, style) -> DrawContext:
        return DrawContext(
            cairo=context.cairo,
            style=style,
            selected=context.selected,
            focused=context.focused,
            hovered=context.hovered,
            dropzone=context.dropzone,
        )

    cairo: CairoContext
    style: Style
    selected: bool
    focused: bool
    hovered: bool
    dropzone: bool


class cairo_state:
    def __init__(self, cr):
        self._cr = cr

    def __enter__(self):
        self._cr.save()
        return self._cr

    def __exit__(self, _type, _value, _traceback):
        self._cr.restore()


def stroke(context: DrawContext, fill=True, highlight=False):
    style = context.style
    cr = context.cairo
    fill_color = style.get("background-color")
    if fill and fill_color:
        with cairo_state(cr):
            cr.set_source_rgba(*fill_color)
            cr.fill_preserve()

    if highlight:
        draw_highlight(context)

    with cairo_state(cr):
        stroke = style.get("color")
        if stroke:
            cr.set_source_rgba(*stroke)
        line_width = style.get("line-width")
        if line_width:
            cr.set_line_width(line_width)
        cr.stroke()


def draw_border(box, context: DrawContext, bounding_box: Rectangle):
    cr = context.cairo
    d = context.style["border-radius"]
    x, y, width, height = bounding_box

    cr.move_to(x, d)
    cr.set_dash(context.style["dash-style"], 0)
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

    stroke(context)


def draw_top_separator(box: Box, context: DrawContext, bounding_box: Rectangle):
    x, y, w, h = bounding_box
    cr = context.cairo
    cr.move_to(x, y)
    cr.line_to(x + w, y)

    stroke(context, fill=False)


def draw_highlight(context: DrawContext):
    if not context.dropzone:
        return
    with cairo_state(context.cairo) as cr:
        highlight_color = context.style["highlight-color"]
        cr.set_source_rgba(*highlight_color)
        cr.set_line_width(cr.get_line_width() * 3.141)
        cr.stroke_preserve()


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

    def __init__(
        self,
        *children,
        style: Style = {},
        draw: Optional[Callable[[Box, DrawContext, Rectangle], None]] = None
    ):
        self.children = children
        self.sizes: List[Tuple[int, int]] = []
        self._inline_style = style
        self._draw_border = draw

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, index):
        return self.children[index]

    def size(self, context: SizeContext):
        style: Style = combined_style(context.style, self._inline_style)
        min_width = style["min-width"]
        min_height = style["min-height"]
        padding_top, padding_right, padding_bottom, padding_left = style["padding"]
        self.sizes = sizes = [c.size(context) for c in self.children]
        if sizes:
            widths, heights = list(zip(*sizes))
            return (
                max(min_width, max(widths) + padding_right + padding_left,),
                max(min_height, sum(heights) + padding_top + padding_bottom,),
            )
        else:
            return min_width, min_height

    def draw(self, context: DrawContext, bounding_box: Rectangle):
        style: Style = combined_style(context.style, self._inline_style)
        new_context = replace(context, style=style)
        padding_top, padding_right, padding_bottom, padding_left = style["padding"]
        valign = style["vertical-align"]
        height = sum(h for _w, h in self.sizes)

        if self._draw_border:
            self._draw_border(self, new_context, bounding_box)
        x = bounding_box.x + padding_left
        if valign is VerticalAlign.MIDDLE:
            y = (
                bounding_box.y
                + padding_top
                + (max(height, bounding_box.height - padding_top) - height) / 2
            )
        elif valign is VerticalAlign.BOTTOM:
            y = bounding_box.y + bounding_box.height - height - padding_bottom
        else:
            y = bounding_box.y + padding_top
        w = bounding_box.width - padding_right - padding_left
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
        self._inline_style = style

    def size(self, context: SizeContext):
        style = combined_style(context.style, self._inline_style)
        min_width = style["min-width"]
        min_height = style["min-height"]
        padding_top, padding_right, padding_bottom, padding_left = style["padding"]
        self.sizes = [c.size(context) for c in self.children]
        width, height = self.icon.size(context)
        return (
            max(min_width, width + padding_right + padding_left),
            max(min_height, height + padding_top + padding_bottom),
        )

    def draw(self, context: DrawContext, bounding_box: Rectangle):
        style = combined_style(context.style, self._inline_style)
        new_context = replace(context, style=style)
        padding_top, padding_right, padding_bottom, padding_left = style["padding"]
        vertical_spacing = style["vertical-spacing"]
        x = bounding_box.x + padding_left
        y = bounding_box.y + padding_top
        w = bounding_box.width - padding_right - padding_left
        h = bounding_box.height - padding_top - padding_bottom
        self.icon.draw(new_context, Rectangle(x, y, w, h))

        # TODO: Change X and initial Y, based on placement. Also change X text-alignment  (left/right/center)
        y = y + bounding_box.height + vertical_spacing
        for c, (cw, ch) in zip(self.children, self.sizes):
            mw = max(w, cw)
            c.draw(context, Rectangle(x - (mw - w) / 2, y, mw, ch))
            y += ch


class Text:
    def __init__(self, text=lambda: "", width=lambda: -1, style: Style = {}):
        self._text = text if callable(text) else lambda: text
        self.width = width if callable(width) else lambda: width
        self._inline_style = style

    def text(self):
        try:
            return self._text()
        except AttributeError:
            return ""

    def size(self, context: SizeContext):
        style = combined_style(context.style, self._inline_style)
        min_w = style["min-width"]
        min_h = style["min-height"]
        padding_top, padding_right, padding_bottom, padding_left = style["padding"]

        width, height = text_size(context.cairo, self.text(), style, self.width())  # type: ignore[type-var]
        return (
            max(min_w, width + padding_right + padding_left),
            max(min_h, height + padding_top + padding_bottom),
        )

    def text_box(self, style: Style, bounding_box: Rectangle) -> Rectangle:
        """Add padding to a bounding box."""
        padding_top, padding_right, padding_bottom, padding_left = style["padding"]
        return Rectangle(
            bounding_box.x + padding_left,
            bounding_box.y + padding_top,
            bounding_box.width - padding_right - padding_left,
            bounding_box.height - padding_top - padding_bottom,
        )

    def draw(
        self, context: DrawContext, bounding_box: Rectangle
    ) -> Tuple[int, int, int, int]:
        """Draw the text, return the location and size."""
        style = combined_style(context.style, self._inline_style)
        min_w = max(style["min-width"], bounding_box.width)
        min_h = max(style["min-height"], bounding_box.height)
        text_align = style["text-align"]
        text_box = self.text_box(style, bounding_box)

        with cairo_state(context.cairo) as cr:
            text_color = style.get("text-color")
            if text_color:
                cr.set_source_rgba(*text_color)

            x, y, w, h = text_draw(
                cr,
                self.text(),
                style,
                lambda w, h: (bounding_box.x, bounding_box.y),
                width=text_box.width,
                default_size=(min_w, min_h),
                text_align=text_align,
            )
        return x, y, w, h


class EditableText(Text):
    def __init__(self, text=lambda: "", width=lambda: -1, style: Style = {}):
        super().__init__(text, width, {"min-width": 30, "min-height": 14, **style})  # type: ignore[misc]
        self.bounding_box = Rectangle()
        self.text_size = (0, 0)

    def size(self, cr):
        s = super().size(cr)
        self.text_size = s
        return s

    def draw(
        self, context: DrawContext, bounding_box: Rectangle
    ) -> Tuple[int, int, int, int]:
        """Draw the editable text."""
        style = combined_style(context.style, self._inline_style)
        x, y, w, h = super().draw(context, bounding_box)
        text_box = self.text_box(style, bounding_box)
        text_align = style["text-align"]
        vertical_align = style["vertical-align"]
        x, y = focus_box_pos(text_box, self.text_size, text_align, vertical_align)
        text_draw_focus_box(context, x, y, *self.text_size)
        self.bounding_box = Rectangle(x, y, width=w, height=h)
        return x, y, w, h


def draw_default_head(context: DrawContext):
    """
    Default head drawer: move cursor to the first handle.
    """
    context.cairo.move_to(0, 0)


def draw_default_tail(context: DrawContext):
    """
    Default tail drawer: draw line to the last handle.
    """
    context.cairo.line_to(0, 0)


def draw_arrow_head(context: DrawContext):
    cr = context.cairo
    cr.set_dash((), 0)
    cr.move_to(15, -6)
    cr.line_to(0, 0)
    cr.line_to(15, 6)
    cr.stroke()
    cr.move_to(0, 0)


def draw_arrow_tail(context: DrawContext):
    cr = context.cairo
    cr.line_to(0, 0)
    cr.stroke()
    cr.move_to(15, -6)
    cr.line_to(0, 0)
    cr.line_to(15, 6)


def text_draw_focus_box(context, x, y, w, h):
    if context.hovered or context.focused:
        with cairo_state(context.cairo) as cr:
            # cr.set_dash(() if context.focused else (2.0, 2.0), 0)
            cr.set_dash((), 0)
            if context.focused:
                cr.set_source_rgb(0.6, 0.6, 0.6)
            else:
                cr.set_source_rgb(0.8, 0.8, 0.8)
            cr.set_line_width(0.5)
            cr.rectangle(x, y, w, h)
            cr.stroke()
