#!/usr/bin/env python

# Copyright (C) 2002-2017 Arjan Molenaar <gaphor@gmail.com>
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
Use case diagram item.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.classifier import ClassifierItem
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_MIDDLE
from .textelement import text_extents
from gaphas.util import path_ellipse

class UseCaseItem(ClassifierItem):
    """
    Presentation of gaphor.UML.UseCase.
    """
    __uml__ = uml2.UseCase
    __style__ = {
        'min-size':   (50, 30),
        'name-align': (ALIGN_CENTER, ALIGN_MIDDLE),
    }

    def __init__(self, id=None):
        super(UseCaseItem, self).__init__(id)
        self.drawing_style = -1


    def pre_update(self, context):
        cr = context.cairo
        text = self.subject.name
        if text:
            width, height = text_extents(cr, text)
            self.min_width, self.min_height = width + 10, height + 20
        super(UseCaseItem, self).pre_update(context)


    def draw(self, context):
        cr = context.cairo

        rx = self.width / 2. 
        ry = self.height / 2.

        cr.move_to(self.width, ry)
        path_ellipse(cr, rx, ry, self.width, self.height)
        cr.stroke()

        super(UseCaseItem, self).draw(context)


# vim:sw=4:et
