"""
Object node item.
"""

import itertools

from gaphas.state import observed, reversible_property
from gaphor import UML

from gaphor.diagram.nameditem import NamedItem
from gaphas.util import text_extents, text_multiline
from gaphas.geometry import Rectangle, distance_rectangle_point


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

    popup_menu = NamedItem.popup_menu + (
        'separator',
        'Ordering', ('ObjectNodeOrderingVisibilty',
            'separator',
            'ObjectNodeOrderingUnordered',
            'ObjectNodeOrderingOrdered',
            'ObjectNodeOrderingLIFO',
            'ObjectNodeOrderingFIFO')
    )

    def __init__(self, id = None):
        NamedItem.__init__(self, id)

        self._tag = '' #TextElement('value', '{ upperBound = %s }', '*')
        self._tag_bounds = None

        self._show_ordering = False

    @observed
    def _set_ordering(self, ordering):
        """
        Set ordering of object node.
        """
        self.subject.ordering = ordering
        self.request_update()

    ordering = reversible_property(lambda s: s.subject.ordering, _set_ordering)

    tag_bounds = property(lambda s: s._tag_bounds)

    @observed
    def _set_show_ordering(self, value):
        #self.preserve_property(pspec.name)
        self._show_ordering = value
        self.request_update()

    show_ordering = reversible_property(lambda s: s._show_ordering, _set_show_ordering)

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
        NamedItem.on_subject_notify(self, pspec, notifiers)
        if self.subject and not self.subject.upperBound:
            self.subject.upperBound = UML.create(UML.LiteralSpecification)
            self.subject.upperBound.value = '*'
        self.request_update()

    def pre_update(self, context):
        """
        Update object node, its ordering and upper bound specification.
        """
        NamedItem.pre_update(self, context)

        if self.subject.upperBound:
            self._tag = '{ upperBound = %s }\n' % self.subject.upperBound.value

        self._tag += '{ ordering = %s }' % self.subject.ordering

        w, h = text_extents(context.cairo, self._tag, multiline=True)
        x = (self.width - w) / 2
        y = self.height + self.style.margin[2]
        self._tag_bounds = Rectangle(x, y, width=w, height=h)

    def point(self, x, y):
        """
        Return the distance from (x, y) to the item.
        """
        d1 = super(ObjectNodeItem, self).point(x, y)
        d2 = distance_rectangle_point(self._tag_bounds, (x, y))
        return min(d1, d2)

    def draw(self, context):
        cr = context.cairo
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

        super(ObjectNodeItem, self).draw(context)

        if self._tag:
            text_multiline(cr, self._tag_bounds[0], self._tag_bounds[1], self._tag)
        if context.hovered or context.focused or context.draw_all:
            cr.set_line_width(0.5)
            b = self._tag_bounds
            cr.rectangle(b.x0, b.y0, b.width, b.height)
            cr.stroke()


# vim:sw=4:et:ai
