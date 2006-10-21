"""
Base classes related to items, which represent those UML classes deriving
from NamedElement.
"""

import itertools

from gaphor.undomanager import get_undo_manager
from gaphor.diagram import DiagramItemMeta
from gaphor.diagram.align import ItemAlign
from gaphor.diagram.diagramitem import DiagramItem
from gaphor.diagram.elementitem import ElementItem

from gaphas.util import text_align, text_extents


class NamedItem(ElementItem):
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
            self.min_width, self.min_height = width + 10, height + 20
        super(NamedItem, self).pre_update(context)


    def draw(self, context):
        """
        Draw item's name.
        """
        c = context.cairo
        rx = self.width / 2.0
        ry = self.height / 2.0

        text = self.subject.name
        if text:
            text_align(c, rx, ry, text, align_x = 0)


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
