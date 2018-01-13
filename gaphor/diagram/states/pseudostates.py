#!/usr/bin/env python

# Copyright (C) 2008-2017 Arjan Molenaar <gaphor@gmail.com>
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
Pseudostate diagram items.

See also gaphor.diagram.states package description.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_TOP
from gaphas.util import path_ellipse
from gaphor.diagram.textelement import text_center
from gaphor.diagram.states import VertexItem


class InitialPseudostateItem(VertexItem):
    """
    Initial pseudostate diagram item.
    """
    __uml__   = uml2.Pseudostate
    __style__ = {
        'min-size':   (20, 20),
        'name-align': (ALIGN_LEFT, ALIGN_TOP),
        'name-padding': (2, 2, 2, 2),
        'name-outside': True,
    }

    RADIUS = 10
    def __init__(self, id=None):
        super(InitialPseudostateItem, self).__init__(id)
        for h in self.handles():
            h.movable = False


    def draw(self, context):
        """
        Draw intial pseudostate symbol.
        """
        super(InitialPseudostateItem, self).draw(context)
        cr = context.cairo
        r = self.RADIUS
        d = r * 2
        path_ellipse(cr, r, r, d, d)
        cr.set_line_width(0.01)
        cr.fill()


class HistoryPseudostateItem(VertexItem):
    """
    History pseudostate diagram item.
    """
    __uml__   = uml2.Pseudostate
    __style__ = {
        'min-size':   (30, 30),
        'name-align': (ALIGN_LEFT, ALIGN_TOP),
        'name-padding': (2, 2, 2, 2),
        'name-outside': True,
    }

    RADIUS = 15
    def __init__(self, id=None):
        super(HistoryPseudostateItem, self).__init__(id)
        for h in self.handles():
            h.movable = False


    def draw(self, context):
        """
        Draw intial pseudostate symbol.
        """
        super(HistoryPseudostateItem, self).draw(context)
        cr = context.cairo
        r = self.RADIUS
        d = r * 2
        path_ellipse(cr, r, r, d, d)
        #cr.set_line_width(1)
        cr.stroke()
        text_center(cr, r, r, "H", self.style.name_font)

# vim:sw=4:et
