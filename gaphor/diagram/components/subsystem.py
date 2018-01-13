#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
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
Subsystem item represents a component with stereotype subsystem (see table
B.1 UML Keywords in UML 2.2 specification).

Subsystem item is part of components Gaphor package because it will show
components, nodes and other items within cotext of a subsystem. 

At the moment (in the future additionally) it makes only sense to use it on
use cases diagram.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.component import ComponentItem
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_TOP
from gaphor.diagram import uml

@uml(uml2.Component, stereotype='subsystem')
class SubsystemItem(ComponentItem):
    __style__   = {
        'name-align': (ALIGN_LEFT, ALIGN_TOP),
    }
    def __init__(self, id=None):
        super(SubsystemItem, self).__init__(id)


    def draw(self, context):
        super(SubsystemItem, self).draw(context)
        cr = context.cairo

        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()


# vim:sw=4:et
