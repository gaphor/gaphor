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
Actor item classes.
"""

from __future__ import absolute_import
from math import pi

from gaphor.UML import uml2
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_BOTTOM
from gaphor.diagram.classifier import ClassifierItem

class ActorItem(ClassifierItem):
    """
    Actor item is a classifier in icon mode.

    Maybe it should be possible to switch to comparment mode in the future.
    """

    __uml__ = uml2.Actor

    HEAD = 11
    ARM  = 19
    NECK = 10
    BODY = 20
    __style__ = {
        'min-size': (ARM * 2, HEAD + NECK + BODY + ARM),
        'name-align': (ALIGN_CENTER, ALIGN_BOTTOM),
        'name-padding': (5, 0, 5, 0),
        'name-outside': True,
    }

    def __init__(self, id = None):
        ClassifierItem.__init__(self, id)

        self.drawing_style = self.DRAW_ICON


    def draw_icon(self, context):
        """
        Draw actor's icon creature.
        """
        super(ActorItem, self).draw(context)

        cr = context.cairo

        head, neck, arm, body = self.HEAD, self.NECK, self.ARM, self.BODY

        fx = self.width / (arm * 2);
        fy = self.height / (head + neck + body + arm)

        x = arm * fx
        y = (head / 2) * fy
        cy = head * fy

        cr.move_to(x + head * fy / 2.0, y)
        cr.arc(x, y, head * fy / 2.0, 0, 2 * pi)

        cr.move_to(x, y + cy / 2)
        cr.line_to(arm * fx, (head + neck + body) * fy)

        cr.move_to(0, (head + neck) * fy)
        cr.line_to(arm * 2 * fx, (head + neck) * fy)

        cr.move_to(0, (head + neck + body + arm) * fy)
        cr.line_to(arm * fx, (head + neck + body) * fy)
        cr.line_to(arm * 2 * fx, (head + neck + body + arm) * fy)
        cr.stroke()


# vim:sw=4:et
