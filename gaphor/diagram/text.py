"""
Support classes for dealing with text.
"""

from enum import Enum
import cairo
from gi.repository import Pango, PangoCairo

from gaphas.freehand import FreeHandCairoContext


class TextAlign(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlign(Enum):
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


class Text:
    def __init__(self, text, style={}):
        self.text = text
        self.style = {
            "min-width": 0,
            "min-height": 0,
            "font": "sans 10",
            "text-align": TextAlign.CENTER,
            "vertical-align": VerticalAlign.MIDDLE,
            **style,
        }.__getitem__

    def size(self, cr):
        min_w = self.style("min-width")
        min_h = self.style("min-height")
        font = self.style("font")

        # TODO: can we create our own Cairo context? Will that be fast enough? And accurate?
        w, h = text_size(cr, self.text, font)
        return max(min_w, w), max(min_h, h)

    def draw(self, cr, bounding_box):
        font = self.style("font")
        text_align = self.style("text-align")
        vertical_align = self.style("vertical-align")

        cr.save()
        try:
            text_draw_in_box(
                cr, bounding_box, self.text, font, text_align, vertical_align
            )
        except:
            cr.restore()


def _text_layout(cr, text, font, width):
    layout = PangoCairo.create_layout(cr)
    if font:
        layout.set_font_description(Pango.FontDescription.from_string(font))
    layout.set_text(text, length=-1)
    layout.set_width(int(width * Pango.SCALE))
    return layout


def text_size(cr, text, font, width=-1):
    if not text:
        return 0, 0
    layout = _text_layout(cr, text, font, width)
    return layout.get_pixel_size()


def text_draw_in_box(cr, bounding_box, text, font, text_align, vertical_align):
    """
    Draw text relative to (x, y).
    text - text to print (utf8)
    font - The font to render in
    bounding_box - width of the bounding box
    text_align - One of enum TextAlign
    vertical_align - One of enum VerticalAlign
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

    if text_align is TextAlign.CENTER:
        x = ((width - w) / 2) + x
    elif text_align is TextAlign.RIGHT:
        x = x + width - w

    if vertical_align is VerticalAlign.MIDDLE:
        y = ((height - h) / 2) + y
    elif vertical_align is VerticalAlign.BOTTOM:
        y = y + height

    cr.move_to(x, y)

    PangoCairo.show_layout(cr, layout)
