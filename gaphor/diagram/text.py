"""
Support classes for dealing with text.
"""

from enum import Enum
import cairo
from gi.repository import Pango, PangoCairo

from gaphas.geometry import Rectangle
from gaphas.freehand import FreeHandCairoContext
from gaphas.painter import CairoBoundingBoxContext


class TextAlign(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlign(Enum):
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


class TextBox:
    def __init__(self, text=lambda: "", style={}):
        self.text = text if callable(text) else lambda: text
        self.style = {
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

        w, h = text_size(cr, self.text(), font)
        return max(min_w, w), max(min_h, h)

    def draw(self, context, bounding_box):
        cr = context.cairo
        min_w = self.style("min-width")
        min_h = self.style("min-height")
        font = self.style("font")
        text_align = self.style("text-align")
        vertical_align = self.style("vertical-align")

        x, y, w, h = text_draw(
            cr,
            self.text(),
            font,
            lambda w, h: text_point_in_box(
                bounding_box, (w, h), text_align, vertical_align
            ),
            width=bounding_box[2],
            default_size=(min_w, min_h),
        )
        _draw_focus_box(context, x, y, w, h)


class FloatingText:
    """
    Text that's part of a line for example.
    """

    def __init__(self, text=lambda: "", style={}):
        self.text = text if callable(text) else lambda: text
        self.style = {
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

        w, h = text_size(cr, self.text(), font)
        return max(min_w, w), max(min_h, h)

    def draw(self, context, points):
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
            lambda w, h: text_point_at_line(
                points, (w, h), text_align, vertical_align, padding
            ),
            default_size=(min_w, min_h),
        )
        _draw_focus_box(context, x, y, w, h)


def _draw_focus_box(context, x, y, w, h):
    if context.hovered or context.focused:
        cr = context.cairo
        cr.save()
        try:
            cr.set_source_rgb(0.6, 0.6, 0.6)
            cr.set_line_width(0.5)
            cr.rectangle(x, y, w, h)
            cr.stroke()
        finally:
            cr.restore()


def text_size(cr, text, font, width=-1, default_size=(0, 0)):
    if not text:
        return default_size

    layout = _text_layout(cr, text, font, width)
    return layout.get_pixel_size()


def text_draw(cr, text, font, calculate_pos, width=-1, default_size=(0, 0)):
    """
    Draw text relative to (x, y).
    text - text to print (utf8)
    font - The font to render in
    calculate_pos - callback for text positioning
    default_size - default text size, when no text is provided
    """

    if text:
        layout = _text_layout(cr, text, font, width)
        w, h = layout.get_pixel_size()
    else:
        layout = None
        w, h = default_size

    x, y = calculate_pos(w, h)

    cr.move_to(x, y)

    if layout:
        _pango_cairo_show_layout(cr, layout)

    return (x, y, w, h)


def _text_layout(cr, text, font, width):
    layout = _pango_cairo_create_layout(cr)
    if font:
        layout.set_font_description(Pango.FontDescription.from_string(font))
    layout.set_text(text, length=-1)
    layout.set_width(int(width * Pango.SCALE))
    return layout


def _pango_cairo_create_layout(cr):
    """
    Deal with different types of contexts that are passed down,
    namely FreeHandCairoContext and CairoBoundingBoxContext.
    PangoCairo expects a true cairo.Context.
    """
    if isinstance(cr, FreeHandCairoContext):
        cr = cr.cr
    elif isinstance(cr, CairoBoundingBoxContext):
        cr = cr._cairo
    else:
        assert isinstance(
            cr, cairo.Context
        ), f"cr should be a true Cairo.Context, not {cr}"

    return PangoCairo.create_layout(cr)


def _pango_cairo_show_layout(cr, layout):
    if isinstance(cr, FreeHandCairoContext):
        PangoCairo.show_layout(cr.cr, layout)
    elif isinstance(cr, CairoBoundingBoxContext):
        w, h = layout.get_pixel_size()
        cr.rel_line_to(w, h)
        cr.stroke()
    else:
        PangoCairo.show_layout(cr, layout)


def text_point_in_box(bounding_box, text_size, text_align, vertical_align):
    x, y, width, height = bounding_box
    w, h = text_size

    if text_align is TextAlign.CENTER:
        x = ((width - w) / 2) + x
    elif text_align is TextAlign.RIGHT:
        x = x + width - w

    if vertical_align is VerticalAlign.MIDDLE:
        y = ((height - h) / 2) + y
    elif vertical_align is VerticalAlign.BOTTOM:
        y = y + height

    return x, y


def text_point_at_line(points, size, text_align, vertical_align, padding):
    """
    Provide a position (x, y) to draw a text close to a line.

    Parameters:
     - points:  the line points, a list of (x, y) points
     - size:    size of the text, a (width, height) tuple
     - text_align: alignment to the line: left, beginning of the line, center, middle and right: end of the line
     - vertical_align: vertical alignment of the text relative to the line
     - padding: text padding, a (top, right, bottom, left) tuple
    """

    if text_align == TextAlign.LEFT:
        p0 = points[0]
        p1 = points[1]
        x, y = _text_point_at_line_end(size, p0, p1, padding)
    elif text_align == TextAlign.CENTER:
        p0, p1 = middle_segment(points)
        x, y = _text_point_at_line_center(size, p0, p1, vertical_align, padding)
    elif text_align == TextAlign.RIGHT:
        p0 = points[-1]
        p1 = points[-2]
        x, y = _text_point_at_line_end(size, p0, p1, padding)

    return x, y


def middle_segment(points):
    """
    Get middle line segment.
    """
    m = len(points) // 2
    assert m - 1 >= 0 and m < len(points)
    return points[m - 1], points[m]


def _text_point_at_line_end(size, p1, p2, padding):
    """
    Calculate position of the text relative to a line defined by points
    p1 and p2. Text is aligned using align and padding information.

    Parameters:
     - size: text size, a (width, height) tuple
     - p1:      beginning of line segment
     - p2:      end of line segment
     - padding: text padding, a (top, right, bottom, left) tuple
    """
    name_dx = 0.0
    name_dy = 0.0
    ofs = 5

    dx = float(p2[0]) - float(p1[0])
    dy = float(p2[1]) - float(p1[1])

    name_w, name_h = size

    if dy == 0:
        rc = 1000.0  # quite a lot...
    else:
        rc = dx / dy
    abs_rc = abs(rc)
    h = dx > 0  # right side of the box
    v = dy > 0  # bottom side

    if abs_rc > 6:
        # horizontal line
        if h:
            name_dx = ofs
            name_dy = -ofs - name_h
        else:
            name_dx = -ofs - name_w
            name_dy = -ofs - name_h
    elif 0 <= abs_rc <= 0.2:
        # vertical line
        if v:
            name_dx = -ofs - name_w
            name_dy = ofs
        else:
            name_dx = -ofs - name_w
            name_dy = -ofs - name_h
    else:
        # Should both items be placed on the same side of the line?
        r = abs_rc < 1.0

        # Find out alignment of text (depends on the direction of the line)
        align_left = h ^ r
        align_bottom = v ^ r
        if align_left:
            name_dx = ofs
        else:
            name_dx = -ofs - name_w
        if align_bottom:
            name_dy = -ofs - name_h
        else:
            name_dy = ofs
    return p1[0] + name_dx, p1[1] + name_dy


# padding
PADDING_TOP, PADDING_RIGHT, PADDING_BOTTOM, PADDING_LEFT = list(range(4))

# hint tuples to move text depending on quadrant
WIDTH_HINT = (0, 0, -1)  # width hint tuple
R_WIDTH_HINT = (-1, -1, 0)  # width hint tuple
PADDING_HINT = (1, 1, -1)  # padding hint tuple

EPSILON = 1e-6


def _text_point_at_line_center(size, p1, p2, vertical_align, padding):
    """
    Calculate position of the text relative to a line defined by points
    p1 and p2. Text is aligned using align and padding information.

    Parameters:
     - size:    text size, a (width, height) tuple
     - p1:      beginning of line
     - p2:      end of line
     - vertical_align:   text align information, from VerticalAlign
     - padding: text padding, a (top, right, bottom, left) tuple
    """
    x0 = (p1[0] + p2[0]) / 2.0
    y0 = (p1[1] + p2[1]) / 2.0
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    if abs(dx) < EPSILON:
        d1 = -1.0
        d2 = 1.0
    elif abs(dy) < EPSILON:
        d1 = 0.0
        d2 = 0.0
    else:
        d1 = dy / dx
        d2 = abs(d1)

    width, height = size

    # move to center and move by delta depending on line angle
    if d2 < 0.5774:  # <0, 30>, <150, 180>, <-180, -150>, <-30, 0>
        # horizontal mode
        w2 = width / 2.0
        hint = w2 * d2

        x = x0 - w2
        if vertical_align == VerticalAlign.TOP:
            y = y0 - height - padding[PADDING_BOTTOM] - hint
        else:
            y = y0 + padding[PADDING_TOP] + hint
    else:
        # much better in case of vertical lines

        # determine quadrant, we are interested in 1 or 3 and 2 or 4
        # see hint tuples below
        h2 = height / 2.0
        q = (d1 > 0) - (d1 < 0)
        if abs(dx) < EPSILON:
            hint = 0
        else:
            hint = h2 / d2

        if vertical_align == VerticalAlign.TOP:
            x = (
                x0
                + PADDING_HINT[q] * (padding[PADDING_LEFT] + hint)
                + width * WIDTH_HINT[q]
            )
        else:
            x = (
                x0
                - PADDING_HINT[q] * (padding[PADDING_RIGHT] + hint)
                + width * R_WIDTH_HINT[q]
            )
        y = y0 - h2

    return x, y
