#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
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
from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram import items
from gaphor.tests.testcase import TestCase

class ObjectNodeTestCase(TestCase):

    def test_object_node(self):
        self.create(items.ObjectNodeItem, uml2.ObjectNode)


    def test_name(self):
        """
        Test updating of object node name
        """
        node = self.create(items.ObjectNodeItem, uml2.ObjectNode)
        node.subject.name = 'Blah'

        self.assertEquals('Blah', node._name.text)

        node.subject = None
        # Undefined


    def test_upper_bound(self):
        """
        TODO: Test upper bound
        """
        pass


    def test_ordering(self):
        """
        Test updating of ObjectNodeItem.ordering.
        """
        node = self.create(items.ObjectNodeItem, uml2.ObjectNode)
        node.subject.ordering = "unordered"

        self.assertEquals('{ ordering = unordered }', node._ordering.text)

        node.show_ordering = True

        self.assertEquals('{ ordering = unordered }', node._ordering.text)


    def test_persistence(self):
        """
        TODO: Test connector item saving/loading
        """
        pass



# vim:sw=4:et:ai
