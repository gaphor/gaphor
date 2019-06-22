"""
Support classes for dealing with text.
"""

import gi

gi.require_version("PangoCairo", "1.0")

from enum import Enum
import cairo
from gi.repository import Pango, PangoCairo

from gaphas.freehand import FreeHandCairoContext


class Text:
    def __init__(self, text, style=None):
        self.text = text
        self.style = style

    def size(self, cr):
        min_w, min_h = hasattr(self.style, "min_size") and self.style.min_size or (0, 0)
        # TODO: can we create our own Cairo context? Will that be fast enough? And accurate?
        w, h = text_size(cr, self.text, self.style.font)
        return max(min_w, w), max(min_h, h)

    def draw(self, cr, bounding_box):
        cr.save()
        try:
            text_draw_in_box(cr, self.text, self.style.font, bounding_box)
        except:
            cr.restore()


def _text_layout(cr, text, font, width):
    layout = PangoCairo.create_layout(cr)
    if font:
        layout.set_font_description(Pango.FontDescription.from_string(font))
    layout.set_text(text, length=-1)
    layout.set_width(int(width * Pango.SCALE))
    return layout


def text_size(cr, text, font=None, width=-1):
    if not text:
        return 0, 0
    layout = _text_layout(cr, text, font, width)
    return layout.get_pixel_size()


def text_draw_in_box(cr, text, font, bounding_box, align_x=0, align_y=0):
    """
    Draw text relative to (x, y).
    text - text to print (utf8)
    font - The font to render in
    bounding_box - width of the bounding box
    align_x - -1 (left), 0 (center), 1 (right), see style.py
    align_y - -1 (top), 0 (middle), 1 (bottom), see style.py
    """
    if len(bounding_box) == 2:
        x, y = bounding_box
        width = 0
        height = 0
    else:
        x, y, width, height = bounding_box

    if isinstance(cr, FreeHandCairoContext):
        cr = cr.cr
    if not isinstance(cr, cairo.Context):
        return
    if not text:
        return

    layout = _text_layout(cr, text, font, width)

    w, h = layout.get_pixel_size()

    if align_x == 0:
        x = ((width - w) / 2) + x
    elif align_x < 0:
        x = x
    else:
        x = x + width

    if align_y == 0:
        y = ((height - h) / 2) + y
    elif align_y < 0:
        y = y
    else:
        y = y + height
    cr.move_to(x, y)

    PangoCairo.show_layout(cr, layout)
