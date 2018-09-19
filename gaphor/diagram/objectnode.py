#!/usr/bin/env python

# Copyright (C) 2005-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License 
# more details.
#
# You should have received a copy of the GNU Library General Public 
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Object node item.
"""

from __future__ import absolute_import

from gaphas.state import observed, reversible_property

from gaphor.UML import uml2
from gaphor.core import inject
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_BOTTOM

DEFAULT_UPPER_BOUND = '*'


class ObjectNodeItem(NamedItem):
    """
    Representation of object node. Object node is ordered and has upper bound
    specification.

    Ordering information can be hidden by user.
    """

    element_factory = inject('element_factory')

    __uml__ = uml2.ObjectNode

    STYLE_BOTTOM = {
        'text-align': (ALIGN_CENTER, ALIGN_BOTTOM),
        'text-outside': True,
        'text-align-group': 'bottom',
    }

    def __init__(self, id=None):
        NamedItem.__init__(self, id)

        self._show_ordering = False

        self._upper_bound = self.add_text('upperBound',
                                          pattern='{ upperBound = %s }',
                                          style=self.STYLE_BOTTOM,
                                          visible=self.is_upper_bound_visible)

        self._ordering = self.add_text('ordering',
                                       pattern='{ ordering = %s }',
                                       style=self.STYLE_BOTTOM,
                                       visible=self._get_show_ordering)

        self.watch('subject<ObjectNode>.upperBound', self.on_object_node_upper_bound) \
            .watch('subject<ObjectNode>.ordering', self.on_object_node_ordering)

    def on_object_node_ordering(self, event):
        if self.subject:
            self._ordering.text = self.subject.ordering
        self.request_update()

    def on_object_node_upper_bound(self, event):
        subject = self.subject
        if subject and subject.upperBound:
            self._upper_bound.text = subject.upperBound
            self.request_update()

    def is_upper_bound_visible(self):
        """
        Do not show upper bound, when it's set to default value.
        """
        subject = self.subject
        return subject and subject.upperBound != DEFAULT_UPPER_BOUND

    @observed
    def _set_show_ordering(self, value):
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

    def postload(self):
        if self.subject and self.subject.upperBound:
            self._upper_bound.text = self.subject.upperBound
        if self.subject and self._show_ordering:
            self.set_ordering(self.subject.ordering)
        super(ObjectNodeItem, self).postload()

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
            if not value:
                value = DEFAULT_UPPER_BOUND

            subject.upperBound = value
            # self._upper_bound.text = value

    def set_ordering(self, value):
        """
        Set object node ordering value.
        """
        subject = self.subject
        subject.ordering = value
        self._ordering.text = value

# vim:sw=4:et:ai
