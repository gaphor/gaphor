#!/usr/bin/env python

# Copyright (C) 2004-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import
import gobject
import gtk


class Wrapbox(gtk.Table):
    """
    A Wrapbox contains a set of items. A wrap box tries to optimize it's
    content by moving elements to a second row if the do not fit on the first.
    And a third and a fourth, depending on the given space.

    The width is given, the height is changed in order to fit all contained
    objects.
    """

    def __init__(self):
        self.__gobject_init__()
        self.resize_idle_id = 0
        self.rows = 1
        self.cols = 1
        self.resize(self.rows, self.cols)
        self.connect('size_allocate', self.on_size_allocate)
        self.children = []

    def calculate_size(self, allocation):
        children = self.children
        max_width = 0
        for c in children:
            size_request = c.size_request()
            #print size_request
            max_width = max(max_width, size_request[0])
        cols = allocation.width / (max_width or 1)
        if cols == 0:
            cols = 1
        rows = len(children) / cols
        if len(children) % cols:
            rows += 1
        return cols, rows

    def set_new_size(self):
        #table = self.table
        table = self
        children = self.children
        if not children:
            return
        rows = self.rows
        cols = self.cols
        for c in children:
            table.remove(c)
        table.resize(rows, cols)
        x = y = 0
        for c in children:
            table.attach(c, left_attach=x, right_attach=x+1, top_attach=y, bottom_attach=y+1)
            x += 1
            if x  == rows:
                x = 0
                y += 1

    def _idle_handler(self):
        try:
            self.set_new_size()
        finally:
            self.resize_idle_id = 0

    def on_size_allocate(self, table, allocation):
        rows, cols = self.calculate_size(allocation)
        #print 'size_allocate', rows, cols
        if not self.resize_idle_id and (rows != self.rows or cols != self.cols):
            #print 'size_allocate', 'setting idle handler'
            self.resize_idle_id = gobject.idle_add(self._idle_handler)
        self.rows = rows
        self.cols = cols

    def add(self, widget):
        assert widget, 'No widget supplied: %s' % widget
        self.cols += 1
        row = self.rows
        col = self.cols
        #self.table.attach(widget, left_attach=col-1, right_attach=col,
        self.attach(widget, left_attach=col-1, right_attach=col,
                          top_attach=row-1, bottom_attach=row)
        self.children.append(widget)

gobject.type_register(Wrapbox)


# vim:sw=4:et
