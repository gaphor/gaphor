"""
Base classes related to items, which represent UML classes deriving
from NamedElement.
"""

from gaphor.diagram.elementitem import ElementItem
from gaphor.diagram.style import get_min_size, ALIGN_CENTER, ALIGN_TOP


class NamedItem(ElementItem):

    __style__ = {
        'min-size'    : (120, 60),
        'name-align'  : (ALIGN_CENTER, ALIGN_TOP),
        'name-padding': (5, 10, 5, 10),
        'name-outside': False,
    }

    def __init__(self, id=None):
        """
        Create named item.
        """
        ElementItem.__init__(self, id)

        self.width  = self.min_width
        self.height = self.min_height
        style = {
                'text-align': self.style.name_align,
                'text-padding': self.style.name_padding,
                'text-outside': self.style.name_outside,
        }
        self._name = self.add_text('name', style=style)


    def on_subject_notify(self, pspec, notifiers=()):
        #log.debug('Class.on_subject_notify(%s, %s)' % (pspec, notifiers))
        ElementItem.on_subject_notify(self, pspec, ('name',) + notifiers)


    def on_subject_notify__name(self, subject, pspec=None):
        self._name.text = subject.name
        self.request_update()


    def pre_update(self, context):
        """
        Update minimal size information using name bounds.
        """
        if not self.style.name_outside:
            bounds = self._name.bounds
            w, h = get_min_size(bounds.width, bounds.height,
                    self.style.min_size, self.style.name_padding)

            self.min_width = max(w, self.min_width)
            self.min_height = max(h, self.min_height)

        super(NamedItem, self).pre_update(context)


# vim:sw=4:et:ai
