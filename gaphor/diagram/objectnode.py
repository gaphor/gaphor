"""
Object node item.
"""

import itertools

from gaphas.state import observed, reversible_property
from gaphor import UML

from gaphor.diagram.nameditem import NamedItem
from gaphas.util import text_extents, text_multiline
from gaphas.geometry import Rectangle, distance_rectangle_point

DEFAULT_UPPER_BOUND = '*'


class ObjectNodeItem(NamedItem):
    """
    Representation of object node. Object node is ordered and has upper bound
    specification.

    Ordering information can be hidden by user.
    """

    __uml__ = UML.ObjectNode

    __style__ = {
        'margin': (10, 10, 10, 10)
    }

    def __init__(self, id = None):
        NamedItem.__init__(self, id)

        self._show_ordering = False

        self._upper_bound = self.add_text('upperBound.value',
            pattern = '{ upperBound = %s }',
            when = self.display_upper_bound)
        self._ordering = self.add_text('ordering',
            pattern = '{ ordering = %s }',
            when = self._get_show_ordering)


    def display_upper_bound(self):
        return self.subject.upperBound.value != DEFAULT_UPPER_BOUND


    @observed
    def _set_ordering(self, ordering):
        """
        Set ordering of object node.
        """
        self.subject.ordering = ordering
        self.request_update()

    ordering = reversible_property(lambda s: s.subject.ordering, _set_ordering)

    @observed
    def _set_show_ordering(self, value):
        #self.preserve_property(pspec.name)
        self._show_ordering = value
        self.request_update()


    def _get_show_ordering(self):
        return self._show_ordering

    show_ordering = reversible_property(_get_show_ordering, _set_show_ordering)

    def save(self, save_func):
        save_func('show-ordering', self._show_ordering)
        super(ObjectNodeItem, self).save(save_func)

    def load(self, name, value):
        if name == 'show-ordering':
            self._show_ordering = eval(value)
        else:
            super(ObjectNodeItem, self).load(name, value)

    def on_subject_notify(self, pspec, notifiers = ()):
        """
        Detect subject changes. If subject is set then set upper bound text
        element subject.
        """
        NamedItem.on_subject_notify(self, pspec,
                ('upperBound', 'upperBound.value', 'ordering') + notifiers)
        self.set_upper_bound(DEFAULT_UPPER_BOUND)
        self.request_update()


    def draw(self, context):
        cr = context.cairo
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

        super(ObjectNodeItem, self).draw(context)


    def set_upper_bound(self, value):
        """
        Set upper bound value of object node.
        """
        subject = self.subject
        if subject:
            if not subject.upperBound:
                subject.upperBound = UML.create(UML.LiteralSpecification)

            if not value:
                value = DEFAULT_UPPER_BOUND

            subject.upperBound.value = value
            self._upper_bound.text = value


    def set_ordering(self, value):
        """
        Set object node ordering value.
        """
        subject = self.subject
        subject.ordering = value
        self._ordering.text = value


    def on_subject_notify__upperBound(self, subject, pspec=None):
        self.request_update()


    def on_subject_notify__upperBound_value(self, subject, pspec=None):
        self.request_update()


    def on_subject_notify__ordering(self, subject, pspec=None):
        self.request_update()



# vim:sw=4:et:ai
