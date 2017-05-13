#!/usr/bin/env python

# Copyright (C) 2002-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#                         syt <noreply@example.com>
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
"""
CommentLine -- A line that connects a comment to another model element.

"""

from __future__ import absolute_import
import gobject
from zope import component

from .diagramline import DiagramLine
from .interfaces import IConnect


class CommentLineItem(DiagramLine):

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)


    def save (self, save_func):
        DiagramLine.save(self, save_func)
    

    def load (self, name, value):
        DiagramLine.load(self, name, value)


    def postload(self):
        DiagramLine.postload(self)


    def unlink(self):
        canvas = self.canvas
        c1 = canvas.get_connection(self.head)
        c2 = canvas.get_connection(self.tail)
        if c1 and c2:
            query = (c1.connected, self)
            adapter = component.queryMultiAdapter(query, IConnect)
            adapter.disconnect(self.head)
        super(CommentLineItem, self).unlink()


    def draw(self, context):
        context.cairo.set_dash((7.0, 5.0), 0)
        DiagramLine.draw(self, context)


# vim: sw=4:et:ai
