"""
Align classes and constants.
"""

import pango

#
# Enums
#

# horizontal elign
H_ALIGN_LEFT, H_ALIGN_CENTER, H_ALIGN_RIGHT = range(3)

# vertical align
V_ALIGN_TOP, V_ALIGN_MIDDLE, V_ALIGN_BOTTOM = range(3)

# margin indices for ItemALign.margin variable
# order like in CSS
MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM, MARGIN_LEFT = range(4)


class ItemAlign(object):
    """
    Diagram item (canvas element based) align and margins.

    By default there is no margin, item is centered on top.
    """
    def __init__(self, **kw):
        super(ItemAlign, self).__init__()

        self.margin  = (0, ) * 4
        self.align   = H_ALIGN_CENTER
        self.valign  = V_ALIGN_TOP
        self.outside = False

        for k, v in kw.items():
            setattr(self, k, v)


    def copy(self):
        """
        Return shallow copy of align object.
        """
        return ItemAlign(**self.__dict__)


    def get_pos(self, text, width, height, iwidth, iheight):
        if self.outside:
            if self.align == H_ALIGN_LEFT:
                x = -width - self.margin[MARGIN_LEFT]
            elif self.align == H_ALIGN_CENTER:
                x = (iwidth - width) / 2
            elif self.align == H_ALIGN_RIGHT:
                x = iwidth + self.margin[MARGIN_RIGHT]
            else:
                assert False

            if self.valign == V_ALIGN_TOP:
                y = -height - self.margin[MARGIN_TOP]
            elif self.valign == V_ALIGN_MIDDLE:
                y = (iheight - height) / 2
            elif self.valign == V_ALIGN_BOTTOM:
                y = iheight + self.margin[MARGIN_BOTTOM]
            else:
                assert False

        else:
            if self.align == H_ALIGN_LEFT:
                x = self.margin[MARGIN_LEFT]
            elif self.align == H_ALIGN_CENTER:
                x = (iwidth - width) / 2
            elif self.align == H_ALIGN_RIGHT:
                x = iwidth - width - self.margin[MARGIN_RIGHT]
            else:
                assert False

            if self.valign == V_ALIGN_TOP:
                y = self.margin[MARGIN_TOP]
            elif self.valign == V_ALIGN_MIDDLE:
                y = (iheight - height) / 2
            elif self.valign == V_ALIGN_BOTTOM:
                y = iheight - height - self.margin[MARGIN_BOTTOM]
            else:
                assert False
        return x, y


    def get_min_size(self, width, height):
        return width + self.margin[MARGIN_RIGHT] + self.margin[MARGIN_LEFT], \
            height + self.margin[MARGIN_TOP] + self.margin[MARGIN_BOTTOM]
