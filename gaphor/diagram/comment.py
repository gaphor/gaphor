#!/usr/bin/env python

# Copyright (C) 2002-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#                         syt <noreply@example.com>
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
CommentItem diagram item
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from .elementitem import ElementItem
from gaphas.item import NW
from .textelement import text_multiline, text_extents


class CommentItem(ElementItem):

    __uml__ = uml2.Comment

    __style__ = {
        'font': 'sans 10'
    }

    EAR=15
    OFFSET=5

    def __init__(self, id=None):
        ElementItem.__init__(self, id)
        self.min_width = CommentItem.EAR + 2 * CommentItem.OFFSET
        self.height = 50
        self.width = 100
        self.watch('subject<Comment>.body')


    def edit(self):
        #self.start_editing(self._body)
        pass


    def pre_update(self, context):
        if not self.subject:
            return
        cr = context.cairo
        e = self.EAR
        o = self.OFFSET
        w, h = text_extents(cr, self.subject.body, self.style.font, width=self.width - e)
        self.min_width = w + e + o * 2
        self.min_height = h + o * 2
        ElementItem.pre_update(self, context)


    def draw(self, context):
        if not self.subject:
            return
        c = context.cairo
        # Width and height, adjusted for line width...
        ox = float(self._handles[NW].pos.x)
        oy = float(self._handles[NW].pos.y)
        w = self.width + ox
        h = self.height + oy
        ear = CommentItem.EAR
        c.move_to(w - ear, oy)
        line_to = c.line_to
        line_to(w - ear, oy + ear)
        line_to(w, oy + ear)
        line_to(w - ear, oy)
        line_to(ox, oy)
        line_to(ox, h)
        line_to(w, h)
        line_to(w, oy + ear)
        c.stroke()
	if self.subject.body:
            off = self.OFFSET
	    # Do not print empty string, since cairo-win32 can't handle it.
            text_multiline(c, off, off, self.subject.body, self.style.font, self.width - ear, self.height)

# vim:sw=4:et:ai
