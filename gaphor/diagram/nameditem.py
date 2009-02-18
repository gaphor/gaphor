"""
Base classes related to items, which represent UML classes deriving
from NamedElement.
"""

from gaphor import UML
from gaphor.UML.interfaces import IAttributeChangeEvent
from gaphor.application import Application
from gaphor.diagram.elementitem import ElementItem
from gaphor.diagram.style import get_min_size, ALIGN_CENTER, ALIGN_TOP
import gaphor.diagram.font as font

class NamedItem(ElementItem):

    __style__ = {
        'min-size'    : (100, 50),
        'name-align'  : (ALIGN_CENTER, ALIGN_TOP),
        'name-padding': (5, 10, 5, 10),
        'name-outside': False,
        'name-align-str': None,
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
                style={'text-align-group': 'stereotype'},
                visible=self.is_namespace_info_visible,
                font=font.FONT_SMALL)

        self._name = self.add_text('name', style={
                    'text-align': self.style.name_align,
                    'text-padding': self.style.name_padding,
                    'text-outside': self.style.name_outside,
                    'text-align-str': self.style.name_align_str,
                    'text-align-group': 'stereotype',
                }, editable=True)

        # size of stereotype, namespace and name text
        self._header_size = 0, 0
        self.watch('subject<NamedElement>.name', self.on_named_element_name)\
            .watch('subject<Namespace>.namespace', self.on_named_element_namespace)


    def is_namespace_info_visible(self):
        """
        Display name space info when it is different, then diagram's or
        parent's namespace.
        """
        subject = self.subject
        canvas = self.canvas

        if not subject or not canvas:
            return False

        if not self._name.is_visible():
            return False

        namespace = subject.namespace
        parent = canvas.get_parent(self)

        # if there is a parent (i.e. interaction)
        if parent and parent.subject \
                and parent.subject.namespace is not namespace:
            return False

        return self._from.text and namespace is not canvas.diagram.namespace


    def on_named_element_name(self, event):
        """
        Callback to be invoked, when named element name is changed.
        """
        self._name.text = self.subject.name
        self.request_update()


    def on_named_element_namespace(self, event):
        """
        Add a line '(from ...)' to the class item if subject's namespace
        is not the same as the namespace of this diagram.
        """
        subject = self.subject
        if subject and subject.namespace:
            self._from.text = subject.namespace.name
        else:
            self._from.text = ''
        self.request_update()


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
