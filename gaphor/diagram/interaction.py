#!/usr/bin/env python

# Copyright (C) 2004-2017 Arjan Molenaar <gaphor@gmail.com>
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
Interaction diagram item.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_TOP

class InteractionItem(NamedItem):

    __uml__ = uml2.Interaction

    __style__ = {
        'min-size': (150, 100),
        'name-align': (ALIGN_TOP, ALIGN_LEFT),
    }

    def draw(self, context):
        cr = context.cairo
        cr.rectangle(0, 0, self.width, self.height)
        super(InteractionItem, self).draw(context)
        # draw pentagon
        w, h = self._header_size
        h2 = h / 2.0
        cr.move_to(0, h)
        cr.line_to(w - 4, h)
        cr.line_to(w, h2)
        cr.line_to(w, 0)
        cr.stroke()


# vim:sw=4:et
