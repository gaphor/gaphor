#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
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
Test implementation (interface realization) item connectors.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram import items
from gaphor.tests import TestCase

class ImplementationTestCase(TestCase):
    def test_non_interface_glue(self):
        """Test non-interface glueing with implementation
        """
        impl = self.create(items.ImplementationItem)
        clazz = self.create(items.ClassItem, uml2.Class)

        glued = self.allow(impl, impl.head, clazz)
        # connecting head to non-interface item is disallowed
        self.assertFalse(glued)


    def test_interface_glue(self):
        """Test interface glueing with implementation
        """
        iface = self.create(items.InterfaceItem, uml2.Interface)
        impl = self.create(items.ImplementationItem)

        glued = self.allow(impl, impl.head, iface)
        self.assertTrue(glued)


    def test_classifier_glue(self):
        """Test classifier glueing with implementation
        """
        impl = self.create(items.ImplementationItem)
        clazz = self.create(items.ClassItem, uml2.Class)

        glued = self.allow(impl, impl.tail, clazz)
        self.assertTrue(glued)


    def test_connection(self):
        """Test connection of class and interface with implementation
        """
        iface = self.create(items.InterfaceItem, uml2.Interface)
        impl = self.create(items.ImplementationItem)
        clazz = self.create(items.ClassItem, uml2.Class)

        self.connect(impl, impl.head, iface)
        self.connect(impl, impl.tail, clazz)

        # check the datamodel
        self.assertTrue(isinstance(impl.subject, uml2.Implementation))
        ct = self.get_connected(impl.head)
        self.assertTrue(ct is iface)
        self.assertTrue(impl.subject is not None)
        self.assertTrue(impl.subject.contract[0] is iface.subject)
        self.assertTrue(impl.subject.implementatingClassifier[0] is clazz.subject)


    def test_reconnection(self):
        """Test reconnection of class and interface with implementation
        """
        iface = self.create(items.InterfaceItem, uml2.Interface)
        c1 = self.create(items.ClassItem, uml2.Class)
        c2 = self.create(items.ClassItem, uml2.Class)
        impl = self.create(items.ImplementationItem)

        # connect: iface -> c1
        self.connect(impl, impl.head, iface)
        self.connect(impl, impl.tail, c1)

        s = impl.subject

        # reconnect: iface -> c2
        self.connect(impl, impl.tail, c2)

        self.assertSame(s, impl.subject)
        self.assertEquals(1, len(impl.subject.contract))
        self.assertEquals(1, len(impl.subject.implementatingClassifier))
        self.assertTrue(iface.subject in impl.subject.contract)
        self.assertTrue(c2.subject in impl.subject.implementatingClassifier)
        self.assertTrue(c1.subject not in impl.subject.implementatingClassifier, impl.subject.implementatingClassifier)



# vim:sw=4:et:ai
