"""NamedItem diagram item
"""
# vim:sw=4:et

import itertools

from zope import interface
from gaphor.interfaces import INamedItemView

from gaphor.undomanager import get_undo_manager
from gaphor.diagram import DiagramItemMeta
from gaphor.diagram.align import ItemAlign
from gaphor.diagram.diagramitem import DiagramItem
from gaphor.diagram.elementitem import ElementItem
from gaphor.diagram.groupable import GroupBase


class Named(object):
    interface.implements(INamedItemView)

    FONT_NAME = 'sans bold 10'

    #def __init__(self):
        #self._name = diacanvas.shape.Text()
        #self._name.set_font_description(pango.FontDescription(self._FONT))
        #self._name.set_alignment(pango.ALIGN_CENTER)
        #self._name.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        #self._name.set_markup(False)

    #
    # DiagramItem subject notification methods
    #
    def on_subject_notify(self, pspec, notifiers = ()):
        """
        Subject change notification callback.
        """
        ElementItem.on_subject_notify(self, pspec, ('name',) + notifiers)


    def on_subject_notify__name(self, subject, pspec):
        """
        Subject name change notification callback.
        """
        assert self.subject is subject
        self.request_update()



class NamedItemMeta(DiagramItemMeta):

    def __init__(self, name, bases, data):
        super(NamedItemMeta, self).__init__(name, bases, data)
        align = ItemAlign() # center, top
        align.outside = self.s_align.outside
        if align.outside:
            align.margin = (2, ) * 4
        if data.get('__icon__', False):
            align.margin = (30, 35, 10, 35) 
            self.s_align.margin = (30, 35, 10, 35) 
        else:
            align.margin = (15, 30) * 2
        self.set_cls_align('n', align, data)

        if not hasattr(self, '__n_align__'):
            align.align = self.s_align.align

        if not hasattr(self, '__n_valign__'):
            align.valign = self.s_align.valign



class NamedItem(ElementItem, Named):
    __metaclass__ = NamedItemMeta

    popup_menu = ElementItem.popup_menu + (
        'RenameItem',
        'separator',
        'EditDelete',
        'ShowElementInTreeView'
    )

    # these values can be overriden
    WIDTH = 120
    HEIGHT = 60

    def __init__(self, id = None):
        ElementItem.__init__(self, id)
        Named.__init__(self)

        #self._border = self.create_border()
        #self._shapes.add(self._border)


    def create_border(self, border = None):
        """
        Create default border.
        """
        #if border is None:
            #border = diacanvas.shape.Path()
        #border.set_line_width(2.0)
        #self.set(width = self.WIDTH, height = self.HEIGHT)
        #return border
        pass

    def draw_border(self):
        """
        Draw border of simple named item, rectangle by default.
        """
        self._border.rectangle((0, 0), (self.width, self.height))


    def get_name_size(self): # fixme: remove this method
        return self.get_text_size(self._name)


    def update_name(self, affine):
        def set_st_pos(text, x, y, width, height):
            text.set_pos((x, y))
            text.set_max_width(width)
            text.set_max_height(height)

        nalign = self.n_align
        salign = self.s_align

        if self._has_stereotype:
            sw, sh = self.get_text_size(self._stereotype)
            nw, nh = self.get_text_size(self._name)

            width = max(sw, nw)
            height = sh + nh

            # set stereotype position
            sx, sy = salign.get_pos(self._stereotype, width, height, self.width, self.height)
            set_st_pos(self._stereotype, sx, sy, sw, sh)

            # place name below stereotype
            nx = sx + (sw - nw) / 2.0
            ny = sy + sh
            set_st_pos(self._name, nx, ny, nw, nh)

            # determine position and size of stereotype and name placed
            # together
            x = min(sx, nx)
            y = sy

            align = salign
        else:
            width, height = self.get_text_size(self._name)
            x, y = nalign.get_pos(self._name, width, height, self.width, self.height)
            set_st_pos(self._name, x, y, width, height)

            align = nalign

        if not align.outside:
            min_width, min_height = align.get_min_size(width, height)
            self.set(min_width = min_width, min_height = min_height)

        return align, x, y, width, height

    def on_update(self, affine):
        align, x, y, width, height = self.update_name(affine)

        ElementItem.on_update(self, affine)

        if align.outside:
            wx, hy = x + width, y + height
            self.set_bounds((min(0, x), min(0, y),
                max(self.width, wx), max(self.height, hy)))

        self.draw_border()
        self.expand_bounds(1.0)

    def on_shape_iter(self):
        return itertools.chain(Named.on_shape_iter(self),
            ElementItem.on_shape_iter(self))
