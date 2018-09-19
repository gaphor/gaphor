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
"""
Grouping functionality allows to nest one item within another item (parent
item). This is useful in several use cases

- artifact deployed within a node
- a class within a package or a component
- composite structures (i.e. component within a node)

The grouping adapters has to implement three methods, see `AbstractGroup`
class.

It is important to note, that grouping adapters can be queried before
instance of an item to be grouped is created. This happens when item
is about to be created. Therefore `AbstractGroup.can_contain` has
to be aware that `AbstractGroup.item` can be null.
"""

from __future__ import absolute_import
from zope import interface, component

from gaphor.UML import uml2
from gaphor.core import inject
from gaphor.diagram import items
from gaphor.diagram.interfaces import IGroup

class AbstractGroup(object):
    """
    Base class for grouping UML objects.

    :Attributes:
     parent
        Parent item, which groups other items.
     item
        Item to be grouped.
    """
    interface.implements(IGroup)

    element_factory = inject('element_factory')

    def __init__(self, parent, item):
        self.parent = parent
        self.item = item


    def can_contain(self):
        """
        Check if parent can contain an item. True by default.
        """
        return True


    def group(self):
        """
        Group an item within parent.
        """
        raise NotImplemented('This is abstract method')


    def ungroup(self):
        """
        Remove item from parent.
        """
        raise NotImplemented('This is abstract method')



class InteractionLifelineGroup(AbstractGroup):
    """
    Add lifeline to interaction.
    """
    def group(self):
        self.parent.subject.lifeline = self.item.subject
        self.parent.canvas.reparent(self.item, self.parent)


    def ungroup(self):
        del self.parent.subject.lifeline[self.item.subject]


component.provideAdapter(factory=InteractionLifelineGroup,
        adapts=(items.InteractionItem, items.LifelineItem))



class NodeGroup(AbstractGroup):
    """
    Add node to another node.
    """
    def group(self):
        self.parent.subject.nestedNode = self.item.subject


    def ungroup(self):
        del self.parent.subject.nestedNode[self.item.subject]


component.provideAdapter(factory=NodeGroup,
        adapts=(items.NodeItem, items.NodeItem))



class NodeComponentGroup(AbstractGroup):
    """
    Add components to node using internal structures.
    """
    def group(self):
        node = self.parent.subject
        component = self.item.subject

        # node attribute
        a1 = self.element_factory.create(uml2.Property)
        a1.aggregation = 'composite'
        # component attribute
        a2 = self.element_factory.create(uml2.Property)

        e1 = self.element_factory.create(uml2.ConnectorEnd)
        e2 = self.element_factory.create(uml2.ConnectorEnd)

        # create connection between node and component
        e1.role = a1
        e2.role = a2
        connector = self.element_factory.create(uml2.Connector)
        connector.end = e1
        connector.end = e2

        # compose component within node
        node.ownedAttribute = a1
        node.ownedConnector = connector
        component.ownedAttribute =  a2


    def ungroup(self):
        node = self.parent.subject
        component = self.item.subject
        for connector in node.ownedConnector:
            e1 = connector.end[0]
            e2 = connector.end[1]
            if e1.role in node.ownedAttribute and e2.role in component.ownedAttribute:
                e1.role.unlink()
                e2.role.unlink()
                e1.unlink()
                e2.unlink()
                connector.unlink()
                log.debug('Removed %s from node %s' % (component, node))


component.provideAdapter(factory=NodeComponentGroup,
        adapts=(items.NodeItem, items.ComponentItem))



class NodeArtifactGroup(AbstractGroup):
    """
    Deploy artifact on node.
    """
    def group(self):
        node = self.parent.subject
        artifact = self.item.subject

        # deploy artifact on node
        deployment = self.element_factory.create(uml2.Deployment)
        node.deployment = deployment
        deployment.deployedArtifact = artifact


    def ungroup(self):
        node = self.parent.subject
        artifact = self.item.subject
        for deployment in node.deployment:
            if deployment.deployedArtifact[0] is artifact:
                deployment.unlink()
                log.debug('Removed %s from node %s' % (artifact, node))


component.provideAdapter(factory=NodeArtifactGroup,
        adapts=(items.NodeItem, items.ArtifactItem))



class SubsystemUseCaseGroup(AbstractGroup):
    """
    Make subsystem a subject of an use case.
    """
    def group(self):
        component = self.parent.subject
        usecase = self.item.subject
        usecase.subject = component


    def ungroup(self):
        component = self.parent.subject
        usecase = self.item.subject
        usecase.subject.remove(component)


component.provideAdapter(factory=SubsystemUseCaseGroup,
        adapts=(items.SubsystemItem, items.UseCaseItem))



class ActivityPartitionsGroup(AbstractGroup):
    """
    Group activity partitions.
    """
    def can_contain(self):
        return not self.parent.subject \
            or (self.parent.subject and len(self.parent.subject.node) == 0)


    def group(self):
        p = self.parent.subject
        sp = self.element_factory.create(uml2.ActivityPartition)
        self.item.subject = sp
        sp.name = 'Swimlane'
        if p:
            p.subpartition = sp
        for k in self.item.canvas.get_children(self.item):
            sp.subpartition = k.subject


    def ungroup(self):
        p = self.parent.subject
        sp = self.item.subject
        if p:
            p.subpartition.remove(sp)
        self.item.subject = None
        for s in sp.subpartition:
            sp.subpartition.remove(s)
        assert len(sp.node) == 0

        # ungroup activity nodes
        canvas = self.item.canvas
        nodes = [n for n in canvas.get_children(self.item) if 
            isinstance(n, (items.ActivityNodeItem, items.ActionItem, items.ObjectNodeItem, items.ForkNodeItem))]
        for n in nodes:
            canvas.reparent(n, None)

        sp.unlink()


component.provideAdapter(factory=ActivityPartitionsGroup,
        adapts=(items.PartitionItem, items.PartitionItem))



class ActivityNodePartitionGroup(AbstractGroup):
    """
    Group activity nodes within activity partition.
    """
    def can_contain(self):
        return self.parent.subject \
            and len(self.parent.subject.subpartition) == 0


    def group(self):
        partition = self.parent.subject
        node = self.item.subject
        partition.node = node


    def ungroup(self):
        partition = self.parent.subject
        node = self.item.subject
        partition.node.remove(node)


component.provideAdapter(factory=ActivityNodePartitionGroup,
        adapts=(items.PartitionItem, items.ActivityNodeItem))
component.provideAdapter(factory=ActivityNodePartitionGroup,
        adapts=(items.PartitionItem, items.ActionItem))
component.provideAdapter(factory=ActivityNodePartitionGroup,
        adapts=(items.PartitionItem, items.ObjectNodeItem))
component.provideAdapter(factory=ActivityNodePartitionGroup,
        adapts=(items.PartitionItem, items.ForkNodeItem))

