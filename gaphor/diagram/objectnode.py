"""
Object node item.
"""

import itertools

import gobject
import pango

import diacanvas
from gaphor import UML
from gaphor import resource
from gaphor.diagram import initialize_item, TextElement
from nameditem import SimpleNamedItem
from gaphor.diagram.groupable import GroupBase, Groupable


class ObjectNodeItem(SimpleNamedItem, GroupBase):
    """
    Representation of object node. Object node is ordered and has upper bound
    specification.

    Ordering information can be hidden by user.
    """

    __metaclass__ = Groupable

    FONT = 'sans 10'
    MARGIN = 10

    node_popup_menu = (
        'separator',
        'Ordering', ('ObjectNodeOrderingVisibilty',
            'separator',
            'ObjectNodeOrderingUnordered',
            'ObjectNodeOrderingOrdered',
            'ObjectNodeOrderingLIFO',
            'ObjectNodeOrderingFIFO')
    )

    __gproperties__ = {
        'show-ordering': (gobject.TYPE_BOOLEAN, 'show ordering',
            'show ordering of object node', False,
            gobject.PARAM_READWRITE),
    }

    def __init__(self, id = None):
        GroupBase.__init__(self, {
            '_upper_bound': TextElement('value', '{ upperBound = %s }', '*'),
        })
        SimpleNamedItem.__init__(self, id)

        self._ordering = diacanvas.shape.Text()
        self._ordering.set_font_description(pango.FontDescription(self.FONT))
        self._ordering.set_alignment(pango.ALIGN_CENTER)
        self._ordering.set_markup(False)

        self._show_ordering = False
        self.set_prop_persistent('show-ordering')


    def on_subject_notify(self, pspec, notifiers = ()):
        """
        Detect subject changes. If subject is set then set upper bound text
        element subject.
        """
        SimpleNamedItem.on_subject_notify(self, pspec, notifiers)
        if self.subject:
            factory = resource(UML.ElementFactory)
            self.subject.upperBound = factory.create(UML.LiteralSpecification)
            self.subject.upperBound.value = '*'
            self._upper_bound.subject = self.subject.upperBound
        else:
            self._upper_bound.subject = None
        self.request_update()


    def get_popup_menu(self):
        return self.popup_menu + self.node_popup_menu


    def do_set_property(self, pspec, value):
        """
        In case of ordering visibility set request update of item.
        """
        if pspec.name == 'show-ordering':
            self.preserve_property(pspec.name)
            self._show_ordering = value
            self.request_update()
        else:
            SimpleNamedItem.do_set_property(self, pspec, value)


    def do_get_property(self, pspec):
        if pspec.name == 'show-ordering':
            return self._show_ordering
        else:
            return SimpleNamedItem.do_get_property(self, pspec)


    def set_ordering(self, ordering):
        """
        Set ordering of object node.
        """
        self.subject.ordering = ordering
        self.request_update()


    def get_ordering(self):
        """
        Determine ordering of object node.
        """
        return self.subject.ordering


    def get_border(self):
        """
        Return border of simple named item.
        """
        return diacanvas.shape.Path()


    def draw_border(self):
        """
        Draw border of simple named item.
        """
        self._border.rectangle((0, 0), (self.width, self.height))


    def on_update(self, affine):
        """
        Update object node, its ordering and upper bound specification.
        """
        SimpleNamedItem.on_update(self, affine)

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
            self._ordering.set_pos((x, self.height + self.MARGIN))

            self._ordering.set_max_width(ord_width)
            self._ordering.set_max_height(ord_height)

            self.set_bounds((min(0, x), 0,
                max(self.width, ord_width), self.height + self.MARGIN + ord_height))
        else:
            ord_width, ord_height = 0, 0

        #
        # upper bound
        #
        ub_width, ub_height = self._upper_bound.get_size()
        x = (self.width - ub_width) / 2
        y = self.height + ord_height + self.MARGIN
        self._upper_bound.update_label(x, y)

        GroupBase.on_update(self, affine)


    def on_shape_iter(self):
        it = SimpleNamedItem.on_shape_iter(self)
        if self.props.show_ordering:
            return itertools.chain(it, iter([self._ordering]))
        else:
            return it



initialize_item(ObjectNodeItem, UML.ObjectNode)
