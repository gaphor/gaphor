"""
Object node item.
"""

import itertools

from gaphor import UML

#from gaphor.diagram import TextElement
#from gaphor.diagram.align import V_ALIGN_MIDDLE
#from gaphor.diagram.groupable import GroupBase
from gaphor.diagram.nameditem import NamedItem


class ObjectNodeItem(NamedItem):
    """
    Representation of object node. Object node is ordered and has upper bound
    specification.

    Ordering information can be hidden by user.
    """

    __uml__      = UML.ObjectNode

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

        self._upper_bound = TextElement('value', '{ upperBound = %s }', '*')
        self.add(self._upper_bound)

        self._ordering = diacanvas.shape.Text()
        self._ordering.set_font_description(pango.FontDescription(font.FONT))
        self._ordering.set_alignment(pango.ALIGN_CENTER)
        self._ordering.set_markup(False)

        self._show_ordering = False

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
        if self.subject:
            factory = UML
            if not self.subject.upperBound:
                self.subject.upperBound = factory.create(UML.LiteralSpecification)
                self.subject.upperBound.value = '*'
            self._upper_bound.subject = self.subject.upperBound
        else:
            self._upper_bound.subject = None
        self.request_update()


    def do_set_property(self, pspec, value):
        """
        Request update of item in case of ordering visibility.
        """
        if pspec.name == 'show-ordering':
            self.preserve_property(pspec.name)
            self._show_ordering = value
            self.request_update()
        else:
            NamedItem.do_set_property(self, pspec, value)


    def do_get_property(self, pspec):
        if pspec.name == 'show-ordering':
            return self._show_ordering
        else:
            return NamedItem.do_get_property(self, pspec)


    def _set_ordering(self, ordering):
        """
        Set ordering of object node.
        """
        self.subject.ordering = ordering
        self.request_update()


    ordering = property(lambda s: s.subject.ordering, _set_ordering)

    def update(self, context):
        """
        Update object node, its ordering and upper bound specification.
        """
        NamedItem.update(self, context)

        if self.subject:
            self._ordering.set_text('{ ordering = %s }' % self.subject.ordering)
        else:
            self._ordering.set_text('')

        # 
        # object ordering
        #
        if self.props.show_ordering:
            # center ordering below border
            ord_width, ord_height = self._ordering.to_pango_layout(True).get_pixel_size()
            x = (self.width - ord_width) / 2
            self._ordering.set_pos((x, self.height + self.style.margin[0]))

            self._ordering.set_max_width(ord_width)
            self._ordering.set_max_height(ord_height)

            self.set_bounds((min(0, x), 0,
                max(self.width, ord_width), self.height + self.style.margin[0] + ord_height))
        else:
            ord_width, ord_height = 0, 0

        #
        # upper bound
        #
        ub_width, ub_height = self._upper_bound.get_size()
        x = (self.width - ub_width) / 2
        y = self.height + ord_height + self.style.margin[0]
        self._upper_bound.update_label(x, y)



    def draw(self, context):
        super(ObjectNodeItem, self).draw(context)

    def on_shape_iter(self):
        it = NamedItem.on_shape_iter(self)
        if self.props.show_ordering:
            return itertools.chain(it, iter([self._ordering]))
        else:
            return it


# vim:sw=4:et:ai
