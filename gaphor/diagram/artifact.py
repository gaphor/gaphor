#!/usr/bin/env python

# Copyright (C) 2004-2017 Arjan Molenaar <gaphor@gmail.com>
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
Artifact item.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.classifier import ClassifierItem

class ArtifactItem(ClassifierItem):

    __uml__  = uml2.Artifact
    __icon__ = True

    __style__ = {
            'name-padding': (10, 25, 10, 10),
    }

    ICON_HEIGHT = 20

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        self.height = 50
        self.width = 120
        # Set drawing style to compartment w/ small icon
        self.drawing_style = self.DRAW_COMPARTMENT_ICON
        self._line = []
        
    def pre_update_compartment_icon(self, context):
        super(ArtifactItem, self).pre_update_compartment_icon(context)
        w = self.ICON_WIDTH
        h = self.ICON_HEIGHT
        ix, iy = self.get_icon_pos()
        ear = 5
        self._line = (
                (ix + w - ear, iy + ear),
                (ix + w, iy + ear),
                (ix + w - ear, iy),
                (ix, iy),
                (ix, iy + h),
                (ix + w, iy + h),
                (ix + w, iy + ear))


    def draw_compartment_icon(self, context):
        cr = context.cairo
        cr.save()
        self.draw_compartment(context)
        cr.restore()

        # draw icon
        w = self.ICON_WIDTH
        h = self.ICON_HEIGHT
        ix, iy = self.get_icon_pos()
        ear = 5
        cr.set_line_width(1.0)
        cr.move_to(ix + w - ear, iy)
        for x, y in self._line:
            cr.line_to(x, y)
        cr.stroke()



# vim:sw=4:et
