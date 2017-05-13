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
Use case inclusion relationship.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.diagramline import DiagramLine

class IncludeItem(DiagramLine):
    """
    Use case inclusion relationship.
    """

    __uml__ = uml2.Include
    __stereotype__ = 'include'

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)

    def draw_head(self, context):
        cr = context.cairo
        cr.set_dash((), 0)
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)
        cr.stroke()
        cr.move_to(0, 0)

    def draw(self, context):
        context.cairo.set_dash((7.0, 5.0), 0)
        super(IncludeItem, self).draw(context)


# vim:sw=4:et
