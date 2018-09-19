#!/usr/bin/env python

# Copyright (C) 2005-2017 Arjan Molenaar <gaphor@gmail.com>
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

class ActivityNodesTestCase(TestCase):

    def test_decision_node(self):
        """Test creation of decision node
        """
        self.create(items.DecisionNodeItem, uml2.DecisionNode)


    def test_fork_node(self):
        """Test creation of fork node
        """
        self.create(items.ForkNodeItem, uml2.ForkNode)


    def test_decision_node_persistence(self):
        """Test saving/loading of decision node
        """
        factory = self.element_factory
        item = self.create(items.DecisionNodeItem, uml2.DecisionNode)

        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, items.DecisionNodeItem))[0]
        self.assertTrue(item.combined is None, item.combined)

        merge_node = factory.create(uml2.MergeNode)
        item.combined = merge_node
        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, items.DecisionNodeItem))[0]
        self.assertTrue(item.combined is not None, item.combined)
        self.assertTrue(isinstance(item.combined, uml2.MergeNode))


    def test_fork_node_persistence(self):
        """Test saving/loading of fork node
        """
        factory = self.element_factory
        item = self.create(items.ForkNodeItem, uml2.ForkNode)

        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, items.ForkNodeItem))[0]
        self.assertTrue(item.combined is None, item.combined)

        merge_node = factory.create(uml2.JoinNode)
        item.combined = merge_node
        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, items.ForkNodeItem))[0]
        self.assertTrue(item.combined is not None, item.combined)
        self.assertTrue(isinstance(item.combined, uml2.JoinNode))


# vim:sw=4:et:ai
