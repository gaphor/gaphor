"""
Support classes for dealing with text.
"""

import gi

gi.require_version("PangoCairo", "1.0")


import cairo
from gi.repository import Pango, PangoCairo

from gaphas.freehand import FreeHandCairoContext


class Text:
    def __init__(self, text, style=None):
        self.text = text
        self.style = style

    def update_extents(self, cr):
        min_w, min_h = hasattr(self.style, "min_size") and self.style.min_size or (0, 0)
        w, h = text_extents(cr, self.text, self.style.font)
        self._width = max(min_w, w)
        self._height = max(min_h, h)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height


def _text_layout(cr, text, font, width):
    layout = PangoCairo.create_layout(cr)
    if font:
        layout.set_font_description(Pango.FontDescription.from_string(font))
    layout.set_text(text, length=-1)
    layout.set_width(int(width * Pango.SCALE))
    # layout.set_height(height)
    return layout


def text_extents(cr, text, font=None, width=-1, height=-1):
    if not text:
        return 0, 0
    layout = _text_layout(cr, text, font, width)
    return layout.get_pixel_size()


def text_align(
    cr,
    x,
    y,
    text,
    font,
    width=-1,
    height=-1,
    align_x=0,
    align_y=0,
    padding_x=0,
    padding_y=0,
):
    """
    Draw text relative to (x, y).
    x, y - coordinates
    text - text to print (utf8)
    font - The font to render in
    width
    height
    align_x - 1 (top), 0 (middle), -1 (bottom)
    align_y - 1 (left), 0 (center), -1 (right)
    padding_x - padding (extra offset), always > 0
    padding_y - padding (extra offset), always > 0
    """
    if isinstance(cr, FreeHandCairoContext):
        cr = cr.cr
    if not isinstance(cr, cairo.Context):
        return
    if not text:
        return

    layout = _text_layout(cr, text, font, width)

    w, h = layout.get_pixel_size()

    if align_x == 0:
        x = 0.5 - (w / 2) + x
    elif align_x < 0:
        x = -w + x - padding_x
    else:
        x = x + padding_x
    if align_y == 0:
        y = 0.5 - (h / 2) + y
    elif align_y < 0:
        y = -h + y - padding_y
    else:
        y = y + padding_y
    cr.move_to(x, y)

    PangoCairo.show_layout(cr, layout)


def text_center(cr, x, y, text, font):
    text_align(cr, x, y, text, font=font, align_x=0, align_y=0)


def text_multiline(cr, x, y, text, font, width=-1, height=-1):
    text_align(
        cr, x, y, text, font=font, width=width, height=height, align_x=1, align_y=1
    )
