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
Component item.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.classifier import ClassifierItem

class ComponentItem(ClassifierItem):

    __uml__  = uml2.Component
    __icon__ = True

    __style__ = {
            'name-padding': (10, 25, 10, 10),
    }

    BAR_WIDTH     = 10
    BAR_HEIGHT    =  5
    BAR_PADDING   =  5

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        # Set drawing style to compartment w// small icon
        self.drawing_style = self.DRAW_COMPARTMENT_ICON

    def draw_compartment_icon(self, context):
        cr = context.cairo
        cr.save()
        self.draw_compartment(context)
        cr.restore()

        ix, iy = self.get_icon_pos()

        cr.set_line_width(1.0)
        cr.rectangle(ix, iy, self.ICON_WIDTH, self.ICON_HEIGHT)
        cr.stroke()

        bx = ix - self.BAR_PADDING
        bar_upper_y = iy + self.BAR_PADDING
        bar_lower_y = iy + self.BAR_PADDING * 3

        color = cr.get_source()
        cr.rectangle(bx, bar_lower_y, self.BAR_WIDTH, self.BAR_HEIGHT)
        cr.set_source_rgb(1,1,1) # white
        cr.fill_preserve()
        cr.set_source(color)
        cr.stroke()

        cr.rectangle(bx, bar_upper_y, self.BAR_WIDTH, self.BAR_HEIGHT)
        cr.set_source_rgb(1,1,1) # white
        cr.fill_preserve()
        cr.set_source(color)
        cr.stroke()



# vim:sw=4:et
