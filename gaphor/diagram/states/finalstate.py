#!/usr/bin/env python

# Copyright (C) 2008-2017 Artur Wroblewski <wrobell@pld-linux.org>
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
Final state diagram item.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.style import ALIGN_RIGHT, ALIGN_BOTTOM
from gaphas.util import path_ellipse

from gaphor.diagram.states import VertexItem


class FinalStateItem(VertexItem):
    __uml__   = uml2.FinalState
    __style__ = {
        'min-size':   (30, 30),
        'name-align': (ALIGN_RIGHT, ALIGN_BOTTOM),
        'name-padding': (2, 2, 2, 2),
        'name-outside': True,
    }

    RADIUS_1 = 10
    RADIUS_2 = 15
    def __init__(self, id=None):
        super(FinalStateItem, self).__init__(id)
        for h in self.handles():
            h.movable = False

    def draw(self, context):
        """
        Draw final state symbol.
        """
        cr = context.cairo
        r = self.RADIUS_2 + 1
        d = self.RADIUS_1 * 2
        path_ellipse(cr, r, r, d, d)
        cr.set_line_width(0.01)
        cr.fill()

        d = r * 2
        path_ellipse(cr, r, r, d, d)
        cr.set_line_width(0.01)
        cr.set_line_width(2)
        cr.stroke()

        super(FinalStateItem, self).draw(context)

# vim:sw=4:et
