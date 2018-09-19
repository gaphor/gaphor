#!/usr/bin/env python

# Copyright (C) 2009-2017 Artur Wroblewski <wrobell@pld-linux.org>
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
Tests for grouping functionality in Gaphor.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.ui.namespace import NamespaceModel
from gaphor.diagram import items

from gaphor.tests import TestCase 

class NodesGroupTestCase(TestCase):
    """
    Nodes grouping tests.
    """

    def test_grouping(self):
        """Test node within another node composition
        """
        n1 = self.create(items.NodeItem, uml2.Node)
        n2 = self.create(items.NodeItem, uml2.Node)

        self.group(n1, n2)

        self.assertTrue(n2.subject in n1.subject.nestedNode)
        self.assertFalse(n1.subject in n2.subject.nestedNode)


    def test_ungrouping(self):
        """Test decomposition of component from node
        """
        n1 = self.create(items.NodeItem, uml2.Node)
        n2 = self.create(items.NodeItem, uml2.Node)

        self.group(n1, n2)
        self.ungroup(n1, n2)

        self.assertFalse(n2.subject in n1.subject.nestedNode)
        self.assertFalse(n1.subject in n2.subject.nestedNode)



class NodeComponentGroupTestCase(TestCase):

    def test_grouping(self):
        """Test component within node composition
        """
        n = self.create(items.NodeItem, uml2.Node)
        c = self.create(items.ComponentItem, uml2.Component)

        self.group(n, c)

        self.assertEquals(1, len(n.subject.ownedAttribute))
        self.assertEquals(1, len(n.subject.ownedConnector))
        self.assertEquals(1, len(c.subject.ownedAttribute))
        self.assertEquals(2, len(self.kindof(uml2.ConnectorEnd)))

        a1 = n.subject.ownedAttribute[0]
        a2 = c.subject.ownedAttribute[0]

        self.assertTrue(a1.isComposite)
        self.assertTrue(a1 in n.subject.part)

        connector = n.subject.ownedConnector[0]
        self.assertTrue(connector.end[0].role is a1)
        self.assertTrue(connector.end[1].role is a2)


    def test_ungrouping(self):
        """Test decomposition of component from node
        """
        n = self.create(items.NodeItem, uml2.Node)
        c = self.create(items.ComponentItem, uml2.Component)

        query = self.group(n, c)
        query = self.ungroup(n, c)

        self.assertEquals(0, len(n.subject.ownedAttribute))
        self.assertEquals(0, len(c.subject.ownedAttribute))
        self.assertEquals(0, len(self.kindof(uml2.Property)))
        self.assertEquals(0, len(self.kindof(uml2.Connector)))
        self.assertEquals(0, len(self.kindof(uml2.ConnectorEnd)))


class NodeArtifactGroupTestCase(TestCase):

    def test_grouping(self):
        """Test artifact within node deployment
        """
        n = self.create(items.NodeItem, uml2.Node)
        a = self.create(items.ArtifactItem, uml2.Artifact)

        self.group(n, a)

        self.assertEquals(1, len(n.subject.deployment))
        self.assertTrue(n.subject.deployment[0].deployedArtifact[0] is a.subject)


    def test_ungrouping(self):
        """Test removal of artifact from node
        """
        n = self.create(items.NodeItem, uml2.Node)
        a = self.create(items.ArtifactItem, uml2.Artifact)

        query = self.group(n, a)
        query = self.ungroup(n, a)

        self.assertEquals(0, len(n.subject.deployment))
        self.assertEquals(0, len(self.kindof(uml2.Deployment)))



class SubsystemUseCaseGroupTestCase(TestCase):

    def test_grouping(self):
        """Test adding an use case to a subsystem
        """
        s = self.create(items.SubsystemItem, uml2.Component)
        uc1 = self.create(items.UseCaseItem, uml2.UseCase)
        uc2 = self.create(items.UseCaseItem, uml2.UseCase)

        self.group(s, uc1)
        self.assertEquals(1, len(uc1.subject.subject))
        self.group(s, uc2)
        self.assertEquals(1, len(uc2.subject.subject))

        # Classifier.useCase is not navigable to UseCase
        #self.assertEquals(2, len(s.subject.useCase))


    def test_grouping_with_namespace(self):
        """Test adding an use case to a subsystem (with namespace)
        """
        namespace = NamespaceModel(self.element_factory)
        s = self.create(items.SubsystemItem, uml2.Component)
        uc = self.create(items.UseCaseItem, uml2.UseCase)

        # manipulate namespace
        c = self.element_factory.create(uml2.Class)
        attribute = self.element_factory.create(uml2.Property)
        c.ownedAttribute = attribute

        self.group(s, uc)
        self.assertEquals(1, len(uc.subject.subject))
        self.assertTrue(s.subject.namespace is not uc.subject)


    def test_ungrouping(self):
        """Test removal of use case from subsystem
        """
        s = self.create(items.SubsystemItem, uml2.Component)
        uc1 = self.create(items.UseCaseItem, uml2.UseCase)
        uc2 = self.create(items.UseCaseItem, uml2.UseCase)

        self.group(s, uc1)
        self.group(s, uc2)

        self.ungroup(s, uc1)
        self.assertEquals(0, len(uc1.subject.subject))
        # Classifier.useCase is not navigable to UseCase
        #self.assertEquals(1, len(s.subject.useCase))

        self.ungroup(s, uc2)
        self.assertEquals(0, len(uc2.subject.subject))
        # Classifier.useCase is not navigable to UseCase
        #self.assertEquals(0, len(s.subject.useCase))



class PartitionGroupTestCase(TestCase):
    def test_no_subpartition_when_nodes_in(self):
        """Test adding subpartition when nodes added
        """
        p = self.create(items.PartitionItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        p1 = self.create(items.PartitionItem)
        p2 = self.create(items.PartitionItem)

        self.group(p, p1)
        self.group(p1, a1)
        self.assertFalse(self.can_group(p1, p2))


    def test_no_nodes_when_subpartition_in(self):
        """Test adding nodes when subpartition added
        """
        p = self.create(items.PartitionItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        p1 = self.create(items.PartitionItem)

        self.group(p, p1)
        self.assertFalse(self.can_group(p, a1))


    def test_action_grouping(self):
        """Test adding action to partition
        """
        p1 = self.create(items.PartitionItem)
        p2 = self.create(items.PartitionItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        a2 = self.create(items.ActionItem, uml2.Action)

        self.assertFalse(self.can_group(p1, a1)) # cannot add to dimension

        self.group(p1, p2)
        self.group(p2, a1)

        self.assertTrue(self.can_group(p2, a1))
        self.assertEquals(1, len(p2.subject.node))
        self.group(p2, a2)
        self.assertEquals(2, len(p2.subject.node))


    def test_subpartition_grouping(self):
        """Test adding subpartition to partition
        """
        p = self.create(items.PartitionItem)
        p1 = self.create(items.PartitionItem)
        p2 = self.create(items.PartitionItem)

        self.group(p, p1)
        self.assertTrue(p.subject is None)
        self.assertTrue(p1.subject is not None)

        self.group(p, p2)
        self.assertTrue(p.subject is None)
        self.assertTrue(p2.subject is not None)


    def test_ungrouping(self):
        """Test action and subpartition removal
        """
        p1 = self.create(items.PartitionItem)
        p2 = self.create(items.PartitionItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        a2 = self.create(items.ActionItem, uml2.Action)

        self.group(p1, p2)

        # group to p2, it is disallowed to p1
        self.group(p2, a1)
        self.group(p2, a2)

        self.ungroup(p2, a1)
        self.assertEquals(1, len(p2.subject.node))
        self.ungroup(p2, a2)
        self.assertEquals(0, len(p2.subject.node))

        self.ungroup(p1, p2)
        self.assertTrue(p1.subject is None, p1.subject)
        self.assertTrue(p2.subject is None, p2.subject)
        self.assertEquals(0, len(self.kindof(uml2.ActivityPartition)))


    def test_ungrouping_with_actions(self):
        """Test subpartition with actions removal
        """
        p1 = self.create(items.PartitionItem)
        p2 = self.create(items.PartitionItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        a2 = self.create(items.ActionItem, uml2.Action)

        self.group(p1, p2)

        # group to p2, it is disallowed to p1
        self.group(p2, a1)
        self.group(p2, a2)

        partition = p2.subject
        assert len(partition.node) == 2, partition.node
        assert 2 == len(p2.canvas.get_children(p2)), p2.canvas.get_children(p2)

        self.ungroup(p1, p2)

        self.assertEquals(0, len(partition.node))
        self.assertEquals(0, len(p2.canvas.get_children(p2)))
        self.assertEquals(0, len(partition.node))


    def test_nested_subpartition_ungrouping(self):
        """Test removal of subpartition with swimlanes
        """
        p1 = self.create(items.PartitionItem)
        p2 = self.create(items.PartitionItem)
        p3 = self.create(items.PartitionItem)
        p4 = self.create(items.PartitionItem)

        self.group(p1, p2)
        self.group(p2, p3)
        self.group(p2, p4)
        self.assertTrue(p2.subject is not None, p2.subject)
        self.assertTrue(p3.subject is not None, p3.subject)
        self.assertTrue(p4.subject is not None, p4.subject)

        self.ungroup(p1, p2)
        self.assertTrue(p1.subject is None, p1.subject)
        self.assertTrue(p2.subject is None, p2.subject)
        self.assertTrue(p3.subject is not None, p3.subject)
        self.assertTrue(p4.subject is not None, p4.subject)
        self.assertEquals(2, len(self.kindof(uml2.ActivityPartition)))


    def test_nested_subpartition_regrouping(self):
        """Test regrouping of subpartition with swimlanes
        """
        p1 = self.create(items.PartitionItem)
        p2 = self.create(items.PartitionItem)
        p3 = self.create(items.PartitionItem)
        p4 = self.create(items.PartitionItem)

        self.group(p1, p2)
        self.group(p2, p3)
        self.group(p2, p4)
        self.assertTrue(p2.subject is not None, p2.subject)
        self.assertTrue(p3.subject is not None, p3.subject)
        self.assertTrue(p4.subject is not None, p4.subject)

        self.ungroup(p1, p2)
        self.assertTrue(p1.subject is None, p1.subject)
        self.assertTrue(p2.subject is None, p2.subject)
        self.assertTrue(p3.subject is not None, p3.subject)
        self.assertTrue(p4.subject is not None, p4.subject)
        self.assertEquals(2, len(self.kindof(uml2.ActivityPartition)))

        self.group(p1, p2)
        self.assertEquals(3, len(self.kindof(uml2.ActivityPartition)))
        self.assertTrue(p2.subject is not None, p2.subject)
        self.assertTrue(p3.subject is not None, p3.subject)
        self.assertTrue(p4.subject is not None, p4.subject)
        self.assertTrue(p3.subject in p2.subject.subpartition, p2.subject.subpartition)
        self.assertTrue(p4.subject in p2.subject.subpartition, p2.subject.subpartition)


