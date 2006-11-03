"""
Base classes related to items, which represent UML classes deriving
from NamedElement.
"""

from gaphas.util import text_extents

from gaphor.diagram.elementitem import ElementItem
from gaphor.diagram.style import get_min_size, get_text_point, \
        ALIGN_CENTER, ALIGN_TOP


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
        self.name_x     = 0
        self.name_y     = 0


    def pre_update(self, context):
        """
        Calculate minimal size of named item.
        """
        cr = context.cairo
        text = self.subject.name
        if text:
            width, height = text_extents(cr, text)
            self.min_width, self.min_height = get_min_size(width, height,
                    self.style.name_padding)
        super(NamedItem, self).pre_update(context)


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
            cr.move_to(self.name_x, self.name_y)
            cr.show_text(text)
        super(NamedItem, self).draw(context)
