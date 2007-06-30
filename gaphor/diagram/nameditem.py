"""
Base classes related to items, which represent UML classes deriving
from NamedElement.
"""

from gaphor.diagram.elementitem import ElementItem
from gaphor.diagram.style import get_min_size, ALIGN_CENTER, ALIGN_TOP
import gaphor.diagram.font as font

class NamedItem(ElementItem):
    __namedelement__ = True

    __style__ = {
        'min-size'    : (100, 50),
        'name-align'  : (ALIGN_CENTER, ALIGN_TOP),
        'name-padding': (5, 10, 5, 10),
        'name-outside': False,
    }

    def __init__(self, id=None):
        """
        Create named item.
        """
        ElementItem.__init__(self, id)

        # create (from ...) text to distinguish diagram items from
        # different namespace
        self._from = self.add_text('from',
                pattern='(from %s)',
                style={ 'text-align-group': 'stereotype' },
                visible=self.is_namespace_info_visible,
                font=font.FONT_SMALL)

        # size of stereotype, namespace and name text
        self._header_size = 0, 0


    def is_namespace_info_visible(self):
        """
        Display name space info when it is different, then diagram
        namespace.
        """
        return self._from.text and \
                self.canvas.diagram.namespace is not self.subject.namespace


    def on_subject_notify(self, pspec, notifiers=()):
        #log.debug('Class.on_subject_notify(%s, %s)' % (pspec, notifiers))
        ElementItem.on_subject_notify(self, pspec,
                ('namespace', 'namespace.name') + notifiers)
        if self.subject:
            self.on_subject_notify__namespace(self.subject)
                                    

    def on_subject_notify__namespace(self, subject, pspec=None):
        """
        Add a line '(from ...)' to the class item if subject's namespace
        is not the same as the namespace of this diagram.
        """
        if self.subject.namespace:
            self._from.text = self.subject.namespace.name
        else:
            self._from.text = ''
        self.request_update()


    def on_subject_notify__namespace_name(self, subject, pspec=None):
        """
        Change the '(from ...)' line if the namespace's name changes.
        """
        self.on_subject_notify__namespace(subject, pspec)


    def pre_update(self, context):
        """
        Calculate minimal size and header size.
        """
        super(NamedItem, self).pre_update(context)

        style = self._name.style

        # we can determine minimal size and header size only
        # when name is aligned inside an item
        if not style.text_outside:
            # at this stage stereotype text group should be already updated
            assert 'stereotype' in self._text_groups_sizes

            nw, nh = self._text_groups_sizes['stereotype']
            self._header_size = get_min_size(nw, nh, self.style.name_padding)

            self.min_width = max(self.style.min_size[0], self._header_size[0])
            self.min_height = max(self.style.min_size[1], self._header_size[1])


# vim:sw=4:et:ai
