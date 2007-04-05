"""
Base classes related to items, which represent UML classes deriving
from NamedElement.
"""

from gaphas.util import text_extents, text_align

from gaphor.diagram.elementitem import ElementItem
from gaphor.diagram.style import get_min_size, get_text_point, \
        ALIGN_CENTER, ALIGN_TOP


class NamedItem(ElementItem):

    __style__ = {
        'min-size'    : (120, 60),
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

    def __init__(self, id=None):
        """
        Create named item.
        """
        ElementItem.__init__(self, id)

        self.width  = self.min_width
        self.height = self.min_height
        self.name_x = 0
        self.name_y = 0
        self._name_size = (0, 0)


    def get_name_size(self):
        """
        Return width, height of the text (including padding)
        """
        return self._name_size

    def update_name_size(self, context):
        """
        Calculate minimal size of named item.
        """
        cr = context.cairo
        text = self.subject.name
        if text and not self.style.name_outside:
            width, height = text_extents(cr, text)
            padding = self.style.name_padding
            self._name_size = width + padding[0] + padding[2], height + padding[1] + padding[3]
#            if self.min_width < self._name_size[0]:
#                self.min_width = self._name_size[0]
#            if self.min_height < self._name_size[1]:
#                self.min_height = self._name_size[1]
#            self.min_width, self.min_height = get_min_size(width, height,
#                    self.style.min_size,
#                    self.style.name_padding)
#
#        super(NamedItem, self).pre_update(context)


    def update(self, context):
        """
        Calculate position of item's name.
        """
        cr = context.cairo
        text = self.subject.name
        if text:
            width, height = text_extents(cr, text)

            self.name_x, self.name_y = get_text_point(text_extents(cr, text),
                    self.width, self.height,
                    self.style.name_align, self.style.name_padding,
                    self.style.name_outside)
        super(NamedItem, self).update(context)


    def draw(self, context):
        """
        Draw item's name.
        """
        cr = context.cairo

        text = self.subject.name
        if text:
            #cr.move_to(self.name_x, self.name_y)
            #cr.show_text(text)
            text_align(cr, self.name_x, self.name_y, text, *self.style.name_align)
        super(NamedItem, self).draw(context)
