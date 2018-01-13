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
ExtensionItem -- Graphical representation of an association.
"""

# TODO: for Extension.postload(): in some cases where the association ends
# are connected to the same Class, the head_end property is connected to the
# tail end and visa versa.

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.diagramline import NamedLine

class ExtensionItem(NamedLine):
    """
    ExtensionItem represents associations. 
    An ExtensionItem has two ExtensionEnd items. Each ExtensionEnd item
    represents a Property (with Property.association == my association).
    """

    __uml__ = uml2.Extension

    def __init__(self, id=None):
        NamedLine.__init__(self, id)
        self.watch('subject<Extension>.ownedEnd')


    def draw_head(self, context):
        cr = context.cairo
        cr.move_to(0, 0)
        cr.line_to(15, -10)
        cr.line_to(15, 10)
        cr.line_to(0, 0)
        cr.set_source_rgb(0, 0, 0)
        cr.fill()
        cr.move_to(15, 0)


# vim:sw=4:et:ai
