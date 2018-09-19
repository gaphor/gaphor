#!/usr/bin/env python

# Copyright (C) 2008-2017 Arjan Molenaar <gaphor@gmail.com>
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
Test classes.
"""

from __future__ import absolute_import
from gaphor.tests import TestCase
from gaphor.UML import uml2
from gaphor.diagram.classes.interface import InterfaceItem


class InterfaceTestCase(TestCase):
    def test_interface_creation(self):
        """Test interface creation
        """
        iface = self.create(InterfaceItem, uml2.Interface)
        self.assertTrue(isinstance(iface.subject, uml2.Interface))

        self.assertTrue(iface._name.is_visible())

        # check style information
        self.assertFalse(iface.style.name_outside)


    def test_changing_to_icon_mode(self):
        """Test interface changing to icon mode
        """
        iface = self.create(InterfaceItem, uml2.Interface)
        iface.drawing_style = iface.DRAW_ICON

        self.assertEquals(iface.DRAW_ICON, iface.drawing_style)

        # default folded mode is provided
        self.assertTrue(iface.FOLDED_PROVIDED, iface.folded)

        # check if style information changed
        self.assertTrue(iface._name.style.text_outside)

        # handles are not movable anymore
        for h in iface.handles():
            self.assertFalse(h.movable)

        # name is visible
        self.assertTrue(iface._name.is_visible())


    def test_changing_to_classifier_mode(self):
        """Test interface changing to classifier mode
        """
        iface = self.create(InterfaceItem, uml2.Interface)
        iface.drawing_style = iface.DRAW_ICON

        iface.drawing_style = iface.DRAW_COMPARTMENT
        self.assertEquals(iface.DRAW_COMPARTMENT, iface.drawing_style)

        # check if style information changed
        self.assertFalse(iface._name.style.text_outside)

        # handles are movable again
        for h in iface.handles():
            self.assertTrue(h.movable)


    def test_assembly_connector_icon_mode(self):
        """Test interface in assembly connector icon mode
        """
        iface = self.create(InterfaceItem, uml2.Interface)
        assert iface._name.is_visible()

        iface.folded = iface.FOLDED_ASSEMBLY
        self.assertFalse(iface._name.is_visible())
        

    def test_folded_interface_persistence(self):
        """Test folded interface saving/loading
        """
        iface = self.create(InterfaceItem, uml2.Interface)

        # note: assembly folded mode..
        iface.folded = iface.FOLDED_REQUIRED

        data = self.save()
        self.load(data)

        interfaces = self.diagram.canvas.select(lambda e: isinstance(e, InterfaceItem))
        self.assertEquals(1, len(interfaces))
        # ... gives provided folded mode on load;
        # correct folded mode is determined by connections, which will be
        # recreated later, i.e. required folded mode will be set when
        # implementation connects to the interface
        self.assertEquals(iface.FOLDED_PROVIDED, interfaces[0].folded)



# vim:sw=4:et:ai
