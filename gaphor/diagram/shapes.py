from __future__ import annotations

import math
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import replace
from enum import Enum
from math import pi
from typing import Callable, Protocol

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext, Element, UpdateContext
from gaphor.core.modeling.diagram import lookup_attribute
from gaphor.core.styling import (
    JustifyContent,
    Number,
    Padding,
    Style,
    StyleNode,
    TextAlign,
    VerticalAlign,
    WhiteSpace,
)
from gaphor.core.styling.inherit import compute_inherited_style
from gaphor.core.styling.pseudo import compute_pseudo_element_style
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
        if line_width := style.get("line-width", 2):
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


class Orientation(Enum):
    VERTICAL = "v"
    HORIZONTAL = "h"


def rectangle_shrink(rect: Rectangle | None, padding: Padding) -> Rectangle:
    if rect is None:
        return Rectangle()

    top, right, bottom, left = padding
    return Rectangle(
        rect.x + left,
        rect.y + top,
        rect.width - left - right,
        rect.height - top - bottom,
    )


class Shape(Iterable, Protocol):
    def size(
        self, context: UpdateContext, bounding_box: Rectangle | None = None
    ) -> tuple[Number, Number]:
        ...

    def draw(self, context: DrawContext, bounding_box: Rectangle) -> None:
        ...


DEFAULT_PADDING = (0, 0, 0, 0)


class Box:
    """A box like shape.

    Style properties:
    - min-height
    - min-width
    - padding: a tuple (top, right, bottom, left)
    - justify-content: alignment of child shapes
    """

    def __init__(
        self,
        *children: Shape,
        orientation: Orientation = Orientation.VERTICAL,
        draw: Callable[[Box, DrawContext, Rectangle], None] | None = None,
    ):
        self.children = children
        self.sizes: list[tuple[Number, Number]] = []
        self._orientation = orientation
        self._draw_border = draw

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, index):
        return self.children[index]

    def size(self, context: UpdateContext, bounding_box: Rectangle | None = None):
        style = context.style
        min_width = style.get("min-width", 0)
        min_height = style.get("min-height", 0)
        padding = style.get("padding", DEFAULT_PADDING)
        new_bounds = rectangle_shrink(bounding_box, padding)

        if self.children:
            child_context = replace(
                context,
                style={k: v for k, v in context.style.items() if k != "padding"},  # type: ignore[arg-type]
            )
            self.sizes = sizes = [
                c.size(child_context, new_bounds) for c in self.children
            ]
            widths, heights = list(zip(*sizes))
            is_vertical = self._orientation == Orientation.VERTICAL
            padding_top, padding_right, padding_bottom, padding_left = padding
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
        return min_width, min_height

    def draw(self, context: DrawContext, bounding_box: Rectangle):
        if self._orientation == Orientation.VERTICAL:
            self.draw_vertical(context, bounding_box)
        else:
            self.draw_horizontal(context, bounding_box)

    def draw_vertical(self, context: DrawContext, bounding_box: Rectangle):
        style = context.style
        padding_top, padding_right, padding_bottom, padding_left = style.get(
            "padding", DEFAULT_PADDING
        )
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
            self._draw_border(self, context, bounding_box)

        if self.children:
            child_context = replace(
                context,
                style={k: v for k, v in context.style.items() if k != "padding"},  # type: ignore[arg-type]
            )
            x = bounding_box.x + padding_left
            w = bounding_box.width - padding_right - padding_left
            last_child = self.children[-1]
            for c, (_w, h) in zip(self.children, sizes):
                if c is last_child and justify_content is JustifyContent.START:
                    h = bounding_box.height - y
                elif h < avg_height:
                    h = avg_height
                c.draw(child_context, Rectangle(x, y, w, h))
                y += h

    def draw_horizontal(self, context: DrawContext, bounding_box: Rectangle):
        style = context.style
        padding_top, padding_right, padding_bottom, padding_left = style.get(
            "padding", DEFAULT_PADDING
        )
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
            self._draw_border(self, context, bounding_box)

        if self.children:
            child_context = replace(
                context,
                style={k: v for k, v in context.style.items() if k != "padding"},  # type: ignore[arg-type]
            )
            y = bounding_box.y + padding_top
            h = bounding_box.height - padding_bottom - padding_top
            last_child = self.children[-1]
            for c, (w, _h) in zip(self.children, sizes):
                if c is last_child and justify_content is JustifyContent.START:
                    w = bounding_box.width - x
                elif w < avg_width:
                    w = avg_width
                c.draw(child_context, Rectangle(x, y, w, h))
                x += w


class IconBox:
    """A special type of box: the icon element is given the full width/height
    and all other shapes are drawn below the main icon shape.

    Style properties:
    - min-height
    - min-width
    - vertical-spacing: spacing between icon and children
    - padding: a tuple (top, right, bottom, left)
    """

    def __init__(self, icon: Shape, *children: Shape):
        self.icon = CssNode("icon", None, icon)
        self.children = children
        self.sizes: list[tuple[Number, Number]] = []

    def __iter__(self):
        return iter((self.icon, *self.children))

    def size(self, context: UpdateContext, bounding_box: Rectangle | None = None):
        style = context.style
        min_width = style.get("min-width", 0)
        min_height = style.get("min-height", 0)
        padding = style.get("padding", DEFAULT_PADDING)

        new_bounds = rectangle_shrink(bounding_box, padding)
        width, height = self.icon.size(context, new_bounds)

        child_context = replace(
            context,
            style={k: v for k, v in context.style.items() if k != "padding"},  # type: ignore[arg-type]
        )
        new_bounds.expand(new_bounds.width * 1.32)
        self.sizes = [c.size(child_context, new_bounds) for c in self.children]

        padding_top, padding_right, padding_bottom, padding_left = padding
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
        style = context.style
        self.icon.draw(
            context,
            rectangle_shrink(bounding_box, style.get("padding", DEFAULT_PADDING)),
        )

        child_context = replace(
            context,
            style={k: v for k, v in context.style.items() if k != "padding"},  # type: ignore[arg-type]
        )
        cx, cy, max_w, _total_h = self.child_pos(style, bounding_box)
        for c, (cw, ch) in zip(self.children, self.sizes):
            c.draw(child_context, Rectangle(cx + (max_w - cw) / 2, cy, cw, ch))
            cy += ch


class Text:
    def __init__(self, text: str | Callable[[], str]):
        self._text = text if callable(text) else lambda: text
        self._layout = Layout()

    def __iter__(self):
        return iter(())

    def text(self, style: Style | None = None):
        try:
            t = self._text()
        except AttributeError:
            t = ""

        if (
            style
            and (after := compute_pseudo_element_style(style, "after"))
            and (content := after.get("content"))
        ):
            return f"{t}{content}"
        return t

    def size(self, context: UpdateContext, bounding_box: Rectangle | None = None):
        style = context.style
        min_w = style.get("min-width", 0)
        min_h = style.get("min-height", 0)
        text_align = style.get("text-align", TextAlign.CENTER)
        white_space = style.get("white-space", WhiteSpace.NORMAL)

        layout = self._layout
        layout.set(
            text=self.text(style),
            font=style,
            width=bounding_box.width
            if bounding_box and white_space == WhiteSpace.NORMAL
            else -1,
            text_align=text_align,
        )
        width, height = layout.size()
        padding_top, padding_right, padding_bottom, padding_left = style.get(
            "padding", DEFAULT_PADDING
        )
        return (
            max(min_w, width + padding_right + padding_left),
            max(min_h, height + padding_top + padding_bottom),
        )

    def draw(self, context: DrawContext, bounding_box: Rectangle):
        """Draw the text, return the location and size."""
        style = context.style
        min_w = max(style.get("min-width", 0), bounding_box.width)
        min_h = max(style.get("min-height", 0), bounding_box.height)
        text_box = rectangle_shrink(bounding_box, style.get("padding", DEFAULT_PADDING))

        with cairo_state(context.cairo) as cr:
            if text_color := style.get("text-color"):
                cr.set_source_rgba(*text_color)
            elif color := style.get("color"):
                cr.set_source_rgba(*color)

            layout = self._layout
            cr.move_to(text_box.x, text_box.y)
            layout.set(font=style)
            layout.show_layout(cr, text_box.width, default_size=(min_w, min_h))


class CssNode:
    """Create custom styling based on the active style and
    an element/class declaration.
    """

    def __init__(
        self,
        name: str,
        element: Element | None,
        child: Shape,
    ):
        self.name = name
        self.element = element
        self.child = child

    def __iter__(self):
        return iter((self.child,))

    def style_node(self, parent: Style | StyleNode) -> StyleNode:
        return StyledCssNode(parent, self)

    def size(
        self, context: UpdateContext, bounding_box: Rectangle | None = None
    ) -> tuple[Number, Number]:
        style = compute_inherited_style(context.style, self.style_node(context.style))
        new_context = replace(context, style=style)

        return self.child.size(new_context, bounding_box)

    def draw(self, context: DrawContext, bounding_box: Rectangle):
        style = compute_inherited_style(context.style, self.style_node(context.style))
        new_context = replace(context, style=style)

        self.child.draw(new_context, bounding_box)


class StyledCssNode:
    def __init__(self, parent: Style | StyleNode, shape: CssNode):
        self._parent: StyleNode | None = (
            parent.get("-gaphor-style-node") if isinstance(parent, dict) else parent  # type: ignore[assignment]
        )
        self._shape = shape
        self.pseudo: str | None = None
        self.dark_mode = self._parent.dark_mode if self._parent else None

    def name(self) -> str:
        return self._shape.name

    def parent(self) -> StyleNode | None:
        return self._parent

    def children(self) -> Iterator[StyleNode]:
        return (
            node.style_node(self)
            for node in traverse_css_nodes(self._shape, only_children=True)
        )

    def attribute(self, name: str) -> str | None:
        if element := self._shape.element:
            return lookup_attribute(element, name)
        return self._parent.attribute(name) if self._parent else None

    def state(self) -> Sequence[str]:
        return ()

    def __hash__(self):
        return hash((self._parent, self._shape))

    def __eq__(self, other):
        return (
            isinstance(other, StyledCssNode)
            and self._parent == other._parent
            and self._shape == other._shape
        )


def traverse_css_nodes(shape: Shape, only_children=False) -> Iterator[CssNode]:
    """Traverse CSS nodes

    Only return the next level of nodes.

    If ``only_children`` is ``True``, start by checking children of shape,
    instead of shape itself.
    """
    if not only_children and isinstance(shape, CssNode):
        yield shape
    else:
        for s in shape:
            yield from traverse_css_nodes(s)
