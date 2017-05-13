#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
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
"""
State transition implementation.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.core import inject
from gaphor.diagram.diagramline import NamedLine
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_RIGHT, ALIGN_TOP


class TransitionItem(NamedLine):
    """
    Representation of state transition.
    """
    __uml__ = uml2.Transition

    __style__ = {
            'name-align': (ALIGN_RIGHT, ALIGN_TOP),
            'name-padding': (5, 15, 5, 5),
    }

    element_factory = inject('element_factory')

    def __init__(self, id = None):
        NamedLine.__init__(self, id)
        self._guard = self.add_text('guard.specification', editable=True)
        self.watch('subject<Transition>.guard<Constraint>.specification', self.on_guard)


    def postload(self):
        """
        Load guard specification information.
        """
        try:
            self._guard.text = self.subject.guard.specification or ''
        except AttributeError:
            self._guard.text = ''
        super(TransitionItem, self).postload()


    def on_guard(self, event):
        try:
            self._guard.text = self.subject.guard.specification or ''
        except AttributeError:
            self._guard.text = ''
        self.request_update()


    def draw_tail(self, context):
        cr = context.cairo
        cr.line_to(0, 0)
        cr.stroke()
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)


# vim:sw=4:et:ai
