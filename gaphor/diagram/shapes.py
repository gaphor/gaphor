from __future__ import annotations

import math
from dataclasses import replace
from enum import Enum
from math import pi
from typing import Callable

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext, UpdateContext
from gaphor.core.styling import (
    JustifyContent,
    Style,
    TextAlign,
    VerticalAlign,
    merge_styles,
)
from gaphor.diagram.text import Layout


class cairo_state:
    def __init__(self, cr):
        self._cr = cr

    def __enter__(self):
        self._cr.save()
        return self._cr

    def __exit__(self, _type, _value, _traceback):
        self._cr.restore()


def stroke(context: DrawContext, fill: bool, dash=True):
    style = context.style
    cr = context.cairo
    fill_color = style.get("background-color")
    if fill and fill_color:
        with cairo_state(cr):
            cr.set_source_rgba(*fill_color)
            cr.fill_preserve()

    with cairo_state(cr):
        if stroke := style.get("color"):
            cr.set_source_rgba(*stroke)
        if line_width := style.get("line-width"):
            cr.set_line_width(line_width)
        if dash:
            cr.set_dash(style.get("dash-style", ()), 0)
        cr.stroke()


def draw_border(box, context: DrawContext, bounding_box: Rectangle):
    cr = context.cairo
    x, y, width, height = bounding_box
    d = min(context.style.get("border-radius", 0), width / 2.0, height / 2.0)

    cr.move_to(x, y + d)
    cr.set_dash(context.style.get("dash-style", ()), 0)
    if d:
        x1 = x + width
        y1 = y + height
        cr.arc(x + d, y + d, d, pi, 1.5 * pi)
        cr.line_to(x1 - d, y)
        cr.arc(x1 - d, y + d, d, 1.5 * pi, 0)
        cr.line_to(x1, y1 - d)
        cr.arc(x1 - d, y1 - d, d, 0, 0.5 * pi)
        cr.line_to(x + d, y1)
        cr.arc(x + d, y1 - d, d, 0.5 * pi, pi)
    else:
        cr.rectangle(x, y, width, height)

    cr.close_path()

    stroke(context, fill=True)


def draw_top_separator(box: Box, context: DrawContext, bounding_box: Rectangle):
    x, y, w, _h = bounding_box
    cr = context.cairo
    cr.move_to(x, y)
    cr.line_to(x + w, y)

    stroke(context, fill=False)


def draw_left_separator(box: Box, context: DrawContext, bounding_box: Rectangle):
    x, y, _w, h = bounding_box
    cr = context.cairo
    cr.move_to(x, y)
    cr.line_to(x, y + h)

    stroke(context, fill=False)


def draw_ellipse(box: Box, context: DrawContext, bounding_box: Rectangle):
    ellipse(context.cairo, *bounding_box)

    stroke(context, fill=True)


def ellipse(cr, x, y, w, h, dc=None):
    if dc is None:
        dc = (4 / 3) * math.tan(math.pi / 8)
    rx = x + w / 2.0
    ry = y + h / 2.0
    x1 = x + w
    y1 = y + h
    tw = w * dc / 2
    th = h * dc / 2

    # curve: control_a, control_b, end
    cr.move_to(x, ry)
    cr.curve_to(x, ry - th, rx - tw, y, rx, y)
    cr.curve_to(rx + tw, y, x1, ry - th, x1, ry)
    cr.curve_to(x1, ry + th, rx + tw, y1, rx, y1)
    cr.curve_to(rx - tw, y1, x, ry + th, x, ry)

    cr.close_path()


class Orientation(Enum):
    VERTICAL = "v"
    HORIZONTAL = "h"


class Box:
    """A box like shape.

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
        orientation: Orientation = Orientation.VERTICAL,
        style: Style | None = None,
        draw: Callable[[Box, DrawContext, Rectangle], None] | None = None,
    ):
        if style is None:
            style = {}
        self.children = children
        self.sizes: list[tuple[int, int]] = []
        self._orientation = orientation
        self._inline_style = style
        self._draw_border = draw

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, index):
        return self.children[index]

    def size(self, context: UpdateContext):
        style = merge_styles(context.style, self._inline_style)
        min_width = style.get("min-width", 0)
        min_height = style.get("min-height", 0)
        padding_top, padding_right, padding_bottom, padding_left = style["padding"]
        self.sizes = sizes = [c.size(context) for c in self.children]
        if sizes:
            widths, heights = list(zip(*sizes))
            is_vertical = self._orientation == Orientation.VERTICAL
            return (
                max(
                    min_width,
                    (max(widths) if is_vertical else sum(widths))
                    + padding_right
                    + padding_left,
                ),
                max(
                    min_height,
                    (sum(heights) if is_vertical else max(heights))
                    + padding_top
                    + padding_bottom,
                ),
            )
        else:
            return min_width, min_height

    def draw(self, context: DrawContext, bounding_box: Rectangle):
        if self._orientation == Orientation.VERTICAL:
            self.draw_vertical(context, bounding_box)
        else:
            self.draw_horizontal(context, bounding_box)

    def draw_vertical(self, context: DrawContext, bounding_box: Rectangle):
        style = merge_styles(context.style, self._inline_style)
        new_context = replace(context, style=style)
        padding_top, padding_right, padding_bottom, padding_left = style["padding"]
        sizes = self.sizes

        justify_content = (
            style.get("justify-content")
            or {
                VerticalAlign.TOP: JustifyContent.START,
                VerticalAlign.MIDDLE: JustifyContent.CENTER,
                VerticalAlign.BOTTOM: JustifyContent.END,
            }[style.get("vertical-align", VerticalAlign.MIDDLE)]
        )

        if justify_content is JustifyContent.STRETCH and sizes:
            height = bounding_box.height
            avg_height = height / len(sizes)
            oversized = [h for _w, h in sizes if h > avg_height]
            d = len(sizes) - len(oversized)
            avg_height = (height - sum(oversized)) / d if d > 0 else 0
        else:
            height = sum(h for _w, h in sizes)
            avg_height = 0

        if justify_content is JustifyContent.CENTER:
            y = (
                bounding_box.y
                + padding_top
                + (max(height, bounding_box.height - padding_top) - height) / 2
            )
        elif justify_content is JustifyContent.END:
            y = bounding_box.y + bounding_box.height - height - padding_bottom
        else:
            y = bounding_box.y + padding_top

        if self._draw_border:
            self._draw_border(self, new_context, bounding_box)

        x = bounding_box.x + padding_left
        w = bounding_box.width - padding_right - padding_left
        if self.children:
            last_child = self.children[-1]
            for c, (_w, h) in zip(self.children, sizes):
                if c is last_child and justify_content is JustifyContent.START:
                    h = bounding_box.height - y
                elif h < avg_height:
                    h = avg_height
                c.draw(context, Rectangle(x, y, w, h))
                y += h

    def draw_horizontal(self, context: DrawContext, bounding_box: Rectangle):
        style = merge_styles(context.style, self._inline_style)
        new_context = replace(context, style=style)
        padding_top, padding_right, padding_bottom, padding_left = style["padding"]
        sizes = self.sizes

        justify_content = style.get("justify-content", JustifyContent.CENTER)

        if justify_content is JustifyContent.STRETCH and sizes:
            width = bounding_box.width
            avg_width = width / len(sizes)
            oversized = [w for w, _h in sizes if w > avg_width]
            d = len(sizes) - len(oversized)
            avg_width = (width - sum(oversized)) / d if d > 0 else 0
        else:
            width = sum(w for w, _h in sizes)
            avg_width = 0

        if justify_content is JustifyContent.CENTER:
            x = (
                bounding_box.x
                + padding_left
                + (max(width, bounding_box.width - padding_left) - width) / 2
            )
        elif justify_content is JustifyContent.END:
            x = bounding_box.x + bounding_box.width - width - padding_right
        else:
            x = bounding_box.x + padding_left

        if self._draw_border:
            self._draw_border(self, new_context, bounding_box)

        y = bounding_box.y + padding_top
        h = bounding_box.height - padding_bottom - padding_top
        if self.children:
            last_child = self.children[-1]
            for c, (w, _h) in zip(self.children, sizes):
                if c is last_child and justify_content is JustifyContent.START:
                    w = bounding_box.height - x
                elif w < avg_width:
                    w = avg_width
                c.draw(context, Rectangle(x, y, w, h))
                x += w


class BoundedBox(Box):
    """A Box.

    It keeps track of the latest bounding box used for drawing.
    """

    def __init__(
        self,
        *children,
        style=None,
        draw: Callable[[Box, DrawContext, Rectangle], None] | None = None,
    ):
        if style is None:
            style = {}
        super().__init__(*children, style=style, draw=draw)
        self.bounding_box = Rectangle()

    def draw(self, context: DrawContext, bounding_box: Rectangle):
        self.bounding_box = bounding_box
        return super().draw(context, bounding_box)

    def __contains__(self, pos_or_rect):
        return pos_or_rect in self.bounding_box


class IconBox:
    """A special type of box: the icon element is given the full width/height
    and all other shapes are drawn below the main icon shape.

    Style properties:
    - min-height
    - min-width
    - vertical-spacing: spacing between icon and children
    - padding: a tuple (top, right, bottom, left)
    """

    def __init__(self, icon, *children, style=None):
        if style is None:
            style = {}
        self.icon = icon
        self.children = children
        self.sizes: list[tuple[int, int]] = []
        self._inline_style = style

    def size(self, context: UpdateContext):
        style = merge_styles(context.style, self._inline_style)
        min_width = style.get("min-width", 0)
        min_height = style.get("min-height", 0)
        padding_top, padding_right, padding_bottom, padding_left = style["padding"]
        self.sizes = [c.size(context) for c in self.children]
        width, height = self.icon.size(context)
        return (
            max(min_width, width + padding_right + padding_left),
            max(min_height, height + padding_top + padding_bottom),
        )

    def child_pos(self, style: Style, bounding_box: Rectangle) -> Rectangle:
        if not self.sizes:
            return Rectangle()

        text_align = style.get("text-align", TextAlign.CENTER)
        vertical_align = style.get("vertical-align", VerticalAlign.BOTTOM)
        vertical_spacing = style.get("vertical-spacing", 0)  # should be margin?

        ws, hs = list(zip(*self.sizes))
        max_w = max(ws)
        total_h = sum(hs)

        if text_align == TextAlign.CENTER:
            x = bounding_box.x + (bounding_box.width - max_w) / 2
        elif text_align == TextAlign.LEFT:
            x = bounding_box.x - max_w - vertical_spacing
        elif text_align == TextAlign.RIGHT:
            x = bounding_box.x + bounding_box.width + vertical_spacing

        if vertical_align == VerticalAlign.BOTTOM:
            y = bounding_box.y + bounding_box.height + vertical_spacing
        elif vertical_align == VerticalAlign.MIDDLE:
            y = bounding_box.y + (bounding_box.height - total_h) / 2
        elif vertical_align == VerticalAlign.TOP:
            y = bounding_box.y - total_h - vertical_spacing
        return Rectangle(
            x,
            y,
            max_w,
            total_h,
        )

    def draw(self, context: DrawContext, bounding_box: Rectangle):
        style = merge_styles(context.style, self._inline_style)
        new_context = replace(context, style=style)
        padding_top, padding_right, padding_bottom, padding_left = style["padding"]
        x = bounding_box.x + padding_left
        y = bounding_box.y + padding_top
        w = bounding_box.width - padding_right - padding_left
        h = bounding_box.height - padding_top - padding_bottom
        self.icon.draw(new_context, Rectangle(x, y, w, h))

        cx, cy, max_w, total_h = self.child_pos(style, bounding_box)
        for c, (cw, ch) in zip(self.children, self.sizes):
            c.draw(context, Rectangle(cx + (max_w - cw) / 2, cy, cw, ch))
            cy += ch


class Text:
    def __init__(self, text=lambda: "", width=lambda: -1, style: Style | None = None):
        if style is None:
            style = {}
        self._text = text if callable(text) else lambda: text
        self.width = width if callable(width) else lambda: width
        self._inline_style = style
        self._layout = Layout()

    def text(self):
        try:
            return self._text()
        except AttributeError:
            return ""

    def size(self, context: UpdateContext):
        style = merge_styles(context.style, self._inline_style)
        min_w = style.get("min-width", 0)
        min_h = style.get("min-height", 0)
        text_align = style.get("text-align", TextAlign.CENTER)
        padding_top, padding_right, padding_bottom, padding_left = style["padding"]

        layout = self._layout
        layout.set(
            text=self.text(), font=style, width=self.width(), text_align=text_align
        )
        width, height = layout.size()
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

    def draw(self, context: DrawContext, bounding_box: Rectangle):
        """Draw the text, return the location and size."""
        style = merge_styles(context.style, self._inline_style)
        min_w = max(style.get("min-width", 0), bounding_box.width)
        min_h = max(style.get("min-height", 0), bounding_box.height)
        text_box = self.text_box(style, bounding_box)

        with cairo_state(context.cairo) as cr:
            if text_color := style.get("text-color"):
                cr.set_source_rgba(*text_color)

            layout = self._layout
            cr.move_to(text_box.x, text_box.y)
            layout.set(font=style)
            layout.show_layout(cr, text_box.width, default_size=(min_w, min_h))


def draw_default_head(context: DrawContext):
    """Default head drawer: move cursor to the first handle."""
    context.cairo.move_to(0, 0)


def draw_default_tail(context: DrawContext):
    """Default tail drawer: draw line to the last handle."""
    context.cairo.line_to(0, 0)


def draw_arrow_head(context: DrawContext):
    cr = context.cairo
    cr.save()
    cr.set_dash((), 0)
    cr.move_to(15, -6)
    cr.line_to(0, 0)
    cr.line_to(15, 6)
    stroke(context, fill=False, dash=False)
    cr.restore()
    cr.move_to(0, 0)


def draw_arrow_tail(context: DrawContext):
    cr = context.cairo
    cr.line_to(0, 0)
    stroke(context, fill=False)
    cr.save()
    cr.set_dash((), 0)
    cr.move_to(15, -6)
    cr.line_to(0, 0)
    cr.line_to(15, 6)
    stroke(context, fill=False, dash=False)
    cr.restore()


def draw_diamond(
    context: DrawContext, x1: float, x2: float, y1: float, y2: float
) -> None:
    """Draw a diamond."""
    cr = context.cairo
    center_x = x1 + (x2 - x1) / 2.0
    center_y = y1 + (y2 - y1) / 2.0
    cr.move_to(x1, center_y)
    cr.line_to(center_x, y2)
    cr.line_to(x2, center_y)
    cr.line_to(center_x, y1)
    cr.line_to(x1, center_y)
    stroke(context, fill=True)
