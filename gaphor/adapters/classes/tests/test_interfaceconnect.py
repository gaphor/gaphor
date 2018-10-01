#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
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
Test connections to folded interface.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram import items
from gaphor.tests import TestCase

class ImplementationTestCase(TestCase):
    def test_folded_interface_connection(self):
        """Test connecting implementation to folded interface
        """
        iface = self.create(items.InterfaceItem, uml2.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        impl = self.create(items.ImplementationItem)

        assert not impl._solid
        self.connect(impl, impl.head, iface, iface.ports()[0])
        self.assertTrue(impl._solid)


    def test_folded_interface_disconnection(self):
        """Test disconnection implementation from folded interface
        """
        iface = self.create(items.InterfaceItem, uml2.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        impl = self.create(items.ImplementationItem)

        assert not impl._solid
        self.connect(impl, impl.head, iface, iface.ports()[0])
        assert impl._solid

        self.disconnect(impl, impl.head)
        self.assertTrue(not impl._solid)


class DependencyTestCase(TestCase):
    def test_folded_interface_connection(self):
        """Test connecting dependency to folded interface
        """
        iface = self.create(items.InterfaceItem, uml2.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        dep = self.create(items.DependencyItem)

        assert not dep._solid
        self.connect(dep, dep.head, iface, iface.ports()[0])
        self.assertTrue(dep._solid)
        # at the end, interface folded notation shall be `required' one
        self.assertEquals(iface.folded, iface.FOLDED_REQUIRED)


    def test_folded_interface_disconnection(self):
        """Test disconnection dependency from folded interface
        """
        iface = self.create(items.InterfaceItem, uml2.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        dep = self.create(items.DependencyItem)

        assert not dep._solid
        self.connect(dep, dep.head, iface, iface.ports()[0])
        assert dep._solid

        self.disconnect(dep, dep.head)
        self.assertTrue(not dep._solid)
        # after disconnection, interface folded notation shall be `provided' one
        self.assertEquals(iface.folded, iface.FOLDED_PROVIDED)


    def test_unfolded_interface_disconnection(self):
        """Test disconnection dependency from unfolded interface
        """
        iface = self.create(items.InterfaceItem, uml2.Interface)
        dep = self.create(items.DependencyItem)

        self.connect(dep, dep.head, iface, iface.ports()[0])
        assert not dep._solid

        self.disconnect(dep, dep.head)
        self.assertTrue(not dep._solid)
        # after disconnection, interface folded property shall be
        # `FOLDED_NONE'
        self.assertEquals(iface.folded, iface.FOLDED_NONE)


LINES = (items.ImplementationItem,
        items.DependencyItem,
        items.GeneralizationItem,
        items.AssociationItem,
        items.CommentLineItem)

class FoldedInterfaceMultipleLinesTestCase(TestCase):
    """
    Test connection of additional diagram lines to folded interface,
    which has already usage dependency or implementation connected.
    """
    def setUp(self):
        super(FoldedInterfaceMultipleLinesTestCase, self).setUp()

        self.iface = self.create(items.InterfaceItem, uml2.Interface)
        self.iface.folded = self.iface.FOLDED_PROVIDED


    def test_interface_with_implementation(self):
        """Test glueing different lines to folded interface with implementation
        """
        impl = self.create(items.ImplementationItem)
        self.connect(impl, impl.head, self.iface, self.iface.ports()[0])

        for cls in LINES:
            line = self.create(cls)
            glued = self.allow(line, line.head, self.iface)
            # no additional lines (specified above) can be glued
            self.assertFalse(glued, 'Glueing of %s should not be allowed' % cls)


    def test_interface_with_dependency(self):
        """Test glueing different lines to folded interface with dependency
        """
        dep = self.create(items.DependencyItem)
        self.connect(dep, dep.head, self.iface, self.iface.ports()[0])

        for cls in LINES:
            line = self.create(cls)
            glued = self.allow(line, line.head, self.iface)
            # no additional lines (specified above) can be glued
            self.assertFalse(glued, 'Glueing of %s should not be allowed' % cls)



class FoldedInterfaceSingleLineTestCase(TestCase):
    """
    Test connection of diagram lines to folded interface. Any lines beside
    implementation and dependency should be forbidden to connect.
    """
    def test_interface_with_forbidden_lines(self):
        """Test glueing forbidden lines to folded interface
        """
        iface = self.create(items.InterfaceItem, uml2.Interface)
        iface.folded = iface.FOLDED_PROVIDED

        for cls in LINES[2:]:
            line = self.create(cls)
            glued = self.allow(line, line.head, iface)
            # no additional lines (specified above) can be glued
            self.assertFalse(glued, 'Glueing of %s should not be allowed' % cls)



# vim:sw=4:et:ai
