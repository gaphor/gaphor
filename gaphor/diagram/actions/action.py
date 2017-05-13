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
Action diagram item.
"""

from __future__ import absolute_import
from math import pi

from gaphor.UML import uml2
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_MIDDLE

class ActionItem(NamedItem):
    __uml__   = uml2.Action
    __style__ = {
        'min-size':   (50, 30),
        'name-align': (ALIGN_CENTER, ALIGN_MIDDLE),
    }


    def draw(self, context):
        """
        Draw action symbol.
        """
        super(ActionItem, self).draw(context)

        c = context.cairo

        d = 15

        c.move_to(0, d)
        c.arc(d, d, d, pi, 1.5 * pi)
        c.line_to(self.width - d, 0)
        c.arc(self.width - d, d, d, 1.5 * pi, 0)
        c.line_to(self.width, self.height - d)
        c.arc(self.width - d, self.height - d, d, 0, 0.5 * pi)
        c.line_to(d, self.height)
        c.arc(d, self.height - d, d, 0.5 * pi, pi)
        c.close_path()

        c.stroke()


class SendSignalActionItem(NamedItem):
    __uml__   = uml2.SendSignalAction
    __style__ = {
        'min-size':   (50, 30),
        'name-align': (ALIGN_CENTER, ALIGN_MIDDLE),
    }


    def draw(self, context):
        """
        Draw action symbol.
        """
        super(SendSignalActionItem, self).draw(context)

        c = context.cairo

        d = 15
        w = self.width
        h = self.height
        c.move_to(0, 0)
        c.line_to(w-d, 0)
        c.line_to(w, h/2)
        c.line_to(w-d, h)
        c.line_to(0, h)
        c.close_path()

        c.stroke()


class AcceptEventActionItem(NamedItem):
    __uml__   = uml2.SendSignalAction
    __style__ = {
        'min-size':   (50, 30),
        'name-align': (ALIGN_CENTER, ALIGN_MIDDLE),
    }


    def draw(self, context):
        """
        Draw action symbol.
        """
        super(AcceptEventActionItem, self).draw(context)

        c = context.cairo

        d = 15
        w = self.width
        h = self.height
        c.move_to(0, 0)
        c.line_to(w, 0)
        c.line_to(w, h)
        c.line_to(0, h)
        c.line_to(d, h/2)
        c.close_path()

        c.stroke()


# vim:sw=4:et:ai
