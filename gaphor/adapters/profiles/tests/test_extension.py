#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
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
Extension item connection adapter tests.
"""

from __future__ import absolute_import
from gaphor.tests import TestCase
from gaphor.UML import uml2
from gaphor.diagram import items

class ExtensionConnectorTestCase(TestCase):
    """
    Extension item connection adapter tests.
    """
    def test_class_glue(self):
        """Test extension item glueing to a class
        """
        ext = self.create(items.ExtensionItem)
        cls = self.create(items.ClassItem, uml2.Class)

        # cannot connect extension item tail to a class
        glued = self.allow(ext, ext.tail, cls)
        self.assertFalse(glued)


    def test_stereotype_glue(self):
        """Test extension item glueing to a stereotype
        """
        ext = self.create(items.ExtensionItem)
        st = self.create(items.ClassItem, uml2.Stereotype)

        # test precondition
        assert type(st.subject) is uml2.Stereotype

        # can connect extension item head to a Stereotype UML metaclass,
        # because it derives from Class UML metaclass
        glued = self.allow(ext, ext.head, st)
        self.assertTrue(glued)


    def test_glue(self):
        """Test extension item glue
        """
        ext = self.create(items.ExtensionItem)
        st = self.create(items.ClassItem, uml2.Stereotype)
        cls = self.create(items.ClassItem, uml2.Class)

        glued = self.allow(ext, ext.tail, st)
        self.assertTrue(glued)

        self.connect(ext, ext.tail, st)

        glued = self.allow(ext, ext.head, cls)
        self.assertTrue(glued)


    def test_connection(self):
        """Test extension item connection
        """
        ext = self.create(items.ExtensionItem)
        st = self.create(items.ClassItem, uml2.Stereotype)
        cls = self.create(items.ClassItem, uml2.Class)

        self.connect(ext, ext.tail, st)
        self.connect(ext, ext.head, cls)
