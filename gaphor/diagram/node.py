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
Node item may represent a node or a device UML metamodel classes.

Grouping
========
Node item can group following items

- other nodes, which are represented with Node.nestedNode on UML metamodel
  level
- deployed artifacts using deployment
- components, which are parts of a node acting as structured classifier
  (nodes may have internal structures)

Node item grouping logic is implemented in `gaphor.adapters.grouping`
module.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.classifier import ClassifierItem

class NodeItem(ClassifierItem):
    """
    Representation of node or device from UML Deployment package.
    """

    __uml__ = uml2.Node, uml2.Device
    __stereotype__ = {
        'device': uml2.Device,
    }

    DEPTH = 10

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        self.drawing_style = self.DRAW_COMPARTMENT
        self.height = 50
        self.width = 120

    def draw_compartment(self, context):
        cr = context.cairo
        cr.save()
        super(NodeItem, self).draw_compartment(context)
        cr.restore()

        d = self.DEPTH
        w = self.width
        h = self.height

        cr.move_to(0, 0)
        cr.line_to(d, -d)
        cr.line_to(w + d, -d)
        cr.line_to(w + d, h - d)
        cr.line_to(w, h)
        cr.move_to(w, 0)
        cr.line_to(w + d, -d)

        cr.stroke()


# vim:sw=4:et
