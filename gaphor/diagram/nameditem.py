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
        self._name = self.add_text('name', style = self.__style__)

        self.name_x = 0
        self.name_y = 0
        self._name_size = (0, 0)


    def on_subject_notify(self, pspec, notifiers=()):
        #log.debug('Class.on_subject_notify(%s, %s)' % (pspec, notifiers))
        ElementItem.on_subject_notify(self, pspec, ('name',) + notifiers)


    def on_subject_notify__name(self, subject, pspec=None):
        self._name.text = subject.name
        self.request_update()


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
