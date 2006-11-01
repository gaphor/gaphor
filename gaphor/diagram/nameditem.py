"""
Base classes related to items, which represent UML classes deriving
from NamedElement.
"""

# padding
PADDING_TOP, PADDING_RIGHT, PADDING_BOTTOM, PADDING_LEFT = range(4)
# horizontal align
ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT = range(3)
# vertical align
ALIGN_TOP, ALIGN_MIDDLE, ALIGN_BOTTOM = range(3)


from gaphor.diagram.elementitem import ElementItem
from gaphas.util import text_align, text_extents


class NamedItem(ElementItem):

    __style__ = {
        'name-align'  : (ALIGN_CENTER, ALIGN_TOP),
        'name-padding': (5, 10, 5, 10),
        'name-outside': False,
    }

    popup_menu = ElementItem.popup_menu + (
        'RenameItem',
        'separator',
        'EditDelete',
        'ShowElementInTreeView'
    )

    def __init__(self, id = None, width = 120, height = 60):
        """
        Create named item.

        Width, height and minimum size is set to default values determined
        by class level @C{WIDTH} and @C{HEIGHT} variables.
        """
        ElementItem.__init__(self, id)

        self.min_width  = width
        self.min_height = height
        self.width      = self.min_width
        self.height     = self.min_height


    def pre_update(self, context):
        """
        Calculate position of item's name.
        """
        cr = context.cairo
        text = self.subject.name
        if text:
            width, height = text_extents(cr, text)
            self.min_width, self.min_height = \
                get_min_size(width, height, self.style.name_padding)
        super(NamedItem, self).pre_update(context)


    def draw(self, context):
        """
        Draw item's name.
        """
        cr = context.cairo

        text = self.subject.name
        if text:
            x, y = get_pos(cr, text, self.width, self.height,
                    self.style.name_align, self.style.name_padding,
                    self.style.name_outside)
            cr.move_to(x, y)
            cr.show_text(text)
        super(NamedItem, self).draw(context)


        

def get_min_size(width, height, padding):
    """
    Get minimum size of an object using padding information.

    @param width: object width
    @param height: object height
    @param padding: padding information as a tuple
        (top, right, bottom, left)

    fixme: move this method outside the class some utility function to
        other package?
    """
    return width + padding[PADDING_LEFT] + padding[PADDING_RIGHT], \
        height + padding[PADDING_TOP] + padding[PADDING_BOTTOM]


def get_pos(cr, text, width, height, align, padding, outside):
    """
    Calculate position of the text relative to containing box defined by
    tuple (0, 0, width, height).  Text is aligned using align and padding
    information. It can be also placed outside the box if @C{outside}
    parameter is set to @C{True}.

    @param width:   width of the containing box
    @param height:  height of the containing box
    @param align:   text align information (center, top, etc.)
    @param padding: text padding
    @param outside: should text be put outside containing box

    fixme: move this method outside the class some utility function to
        other package?
    """
    assert text

    x_bear, y_bear, w, h, x_adv, y_adv = cr.text_extents(text)

    halign, valign = align

    if outside:
        if halign == ALIGN_LEFT:
            x = -w - padding[PADDING_LEFT]
        elif halign == ALIGN_CENTER:
            x = (width - w) / 2
        elif halign == ALIGN_RIGHT:
            x = width + padding[PADDING_RIGHT]
        else:
            assert False

        if valign == ALIGN_TOP:
            y = -h - padding[PADDING_TOP]
        elif valign == ALIGN_MIDDLE:
            y = (height - h) / 2
        elif valign == ALIGN_BOTTOM:
            y = height + padding[PADDING_BOTTOM]
        else:
            assert False

    else:
        if halign == ALIGN_LEFT:
            x = padding[PADDING_LEFT]
        elif halign == ALIGN_CENTER:
            x = (width - w) / 2
        elif halign == ALIGN_RIGHT:
            x = width - w - padding[PADDING_RIGHT]
        else:
            assert False

        if valign == ALIGN_TOP:
            y = h + padding[PADDING_TOP]
        elif valign == ALIGN_MIDDLE:
            y = (height + h) / 2
        elif valign == ALIGN_BOTTOM:
            y = height - h - padding[PADDING_BOTTOM]
        else:
            assert False
    return x, y


# maybe useful for align routines, we will see
###A###    def update_name(self, affine):
###A###        def set_st_pos(text, x, y, width, height):
###A###            text.set_pos((x, y))
###A###            text.set_max_width(width)
###A###            text.set_max_height(height)
###A###
###A###        nalign = self.n_align
###A###        salign = self.s_align
###A###
###A###        if self._has_stereotype:
###A###            sw, sh = self.get_text_size(self._stereotype)
###A###            nw, nh = self.get_text_size(self._name)
###A###
###A###            width = max(sw, nw)
###A###            height = sh + nh
###A###
###A###            # set stereotype position
###A###            sx, sy = salign.get_pos(self._stereotype, width, height, self.width, self.height)
###A###            set_st_pos(self._stereotype, sx, sy, sw, sh)
###A###
###A###            # place name below stereotype
###A###            nx = sx + (sw - nw) / 2.0
###A###            ny = sy + sh
###A###            set_st_pos(self._name, nx, ny, nw, nh)
###A###
###A###            # determine position and size of stereotype and name placed
###A###            # together
###A###            x = min(sx, nx)
###A###            y = sy
###A###
###A###            align = salign
###A###        else:
###A###            width, height = self.get_text_size(self._name)
###A###            x, y = nalign.get_pos(self._name, width, height, self.width, self.height)
###A###            set_st_pos(self._name, x, y, width, height)
###A###
###A###            align = nalign
###A###
###A###        if not align.outside:
###A###            min_width, min_height = align.get_min_size(width, height)
###A###            self.set(min_width = min_width, min_height = min_height)
###A###
###A###        return align, x, y, width, height
###A###
###A###    def on_update(self, affine):
###A###        align, x, y, width, height = self.update_name(affine)
###A###
###A###        ElementItem.on_update(self, affine)
###A###
###A###        if align.outside:
###A###            wx, hy = x + width, y + height
###A###            self.set_bounds((min(0, x), min(0, y),
###A###                max(self.width, wx), max(self.height, hy)))
###A###
###A###        self.draw_border()
###A###        self.expand_bounds(1.0)


# vim:sw=4:et
