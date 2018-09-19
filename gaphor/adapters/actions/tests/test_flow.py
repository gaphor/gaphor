#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
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
Flow item connection adapters tests.
"""

from __future__ import absolute_import
from gaphor.tests import TestCase
from gaphor.UML import uml2
from gaphor.diagram import items

class FlowItemBasicNodesConnectionTestCase(TestCase):
    """
    Tests for flow item connecting to basic activity nodes.
    """
    def test_initial_node_glue(self):
        """Test flow item glueing to initial node item
        """
        flow = self.create(items.FlowItem)
        node = self.create(items.InitialNodeItem, uml2.InitialNode)

        # tail may not connect to initial node item
        allowed = self.allow(flow, flow.tail, node)
        self.assertFalse(allowed)

        allowed = self.allow(flow, flow.head, node)
        self.assertTrue(allowed)


    def test_flow_final_node_glue(self):
        """Test flow item glueing to flow final node item
        """
        flow = self.create(items.FlowItem)
        node = self.create(items.FlowFinalNodeItem, uml2.FlowFinalNode)

        # head may not connect to flow final node item
        allowed = self.allow(flow, flow.head, node)
        self.assertFalse(allowed)

        allowed = self.allow(flow, flow.tail, node)
        self.assertTrue(allowed)


    def test_activity_final_node_glue(self):
        """Test flow item glueing to activity final node item
        """
        flow = self.create(items.FlowItem)
        node = self.create(items.ActivityFinalNodeItem, uml2.ActivityFinalNode)

        # head may not connect to activity final node item
        glued = self.allow(flow, flow.head, node)
        self.assertFalse(glued)

        glued = self.allow(flow, flow.tail, node)
        self.assertTrue(glued)


class FlowItemObjectNodeTestCase(TestCase):
    """
    Flow item connecting to object node item tests.
    """
    def test_glue(self):
        """Test glueing to object node
        """
        flow = self.create(items.FlowItem)
        onode = self.create(items.ObjectNodeItem, uml2.ObjectNode)
        glued = self.allow(flow, flow.head, onode)
        self.assertTrue(glued)


    def test_connection(self):
        """Test connection to object node
        """
        flow = self.create(items.FlowItem)
        anode = self.create(items.ActionItem, uml2.Action)
        onode = self.create(items.ObjectNodeItem, uml2.ObjectNode)

        self.connect(flow, flow.head, anode)
        self.connect(flow, flow.tail, onode)
        self.assertTrue(flow.subject)
        self.assertTrue(isinstance(flow.subject, uml2.ObjectFlow))

        self.disconnect(flow, flow.head)
        self.disconnect(flow, flow.tail)

        # opposite connection
        self.connect(flow, flow.head, onode)
        self.connect(flow, flow.tail, anode)
        self.assertTrue(flow.subject)
        self.assertTrue(isinstance(flow.subject, uml2.ObjectFlow))


    def test_reconnection(self):
        """Test object flow reconnection
        """
        flow = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        o1 = self.create(items.ObjectNodeItem, uml2.ObjectNode)
        o2 = self.create(items.ObjectNodeItem, uml2.ObjectNode)

        # connect: a1 -> o1
        self.connect(flow, flow.head, a1)
        self.connect(flow, flow.tail, o1)

        f = flow.subject
        f.name = 'tname'
        f.guard = 'tguard'

        # reconnect: a1 -> o2
        self.connect(flow, flow.tail, o2)

        self.assertEquals(0, len(a1.subject.incoming))
        self.assertEquals(1, len(a1.subject.outgoing))
        # no connections to o1
        self.assertEquals(0, len(o1.subject.incoming))
        self.assertEquals(0, len(o1.subject.outgoing))
        # connections to o2 instead
        self.assertEquals(1, len(o2.subject.incoming))
        self.assertEquals(0, len(o2.subject.outgoing))

        self.assertEquals(1, len(self.kindof(uml2.ObjectFlow)))
        # one guard
        self.assertEquals('tname', flow.subject.name)
        self.assertEquals('tguard', flow.subject.guard)


    def test_control_flow_reconnection(self):
        """Test control flow becoming object flow due to reconnection
        """
        flow = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        a2 = self.create(items.ActionItem, uml2.Action)
        o1 = self.create(items.ObjectNodeItem, uml2.ObjectNode)

        # connect with control flow: a1 -> a2
        self.connect(flow, flow.head, a1)
        self.connect(flow, flow.tail, a2)

        f = flow.subject
        f.name = 'tname'
        f.guard = 'tguard'

        # reconnect with object flow: a1 -> o1
        self.connect(flow, flow.tail, o1)

        self.assertEquals(0, len(a1.subject.incoming))
        self.assertEquals(1, len(a1.subject.outgoing))
        # no connections to a2
        self.assertEquals(0, len(a2.subject.incoming))
        self.assertEquals(0, len(a2.subject.outgoing))
        # connections to o1 instead
        self.assertEquals(1, len(o1.subject.incoming))
        self.assertEquals(0, len(o1.subject.outgoing))

        self.assertEquals(0, len(self.kindof(uml2.ControlFlow)))
        self.assertEquals(1, len(self.kindof(uml2.ObjectFlow)))
        # one guard, not changed
        self.assertEquals('tname', flow.subject.name)
        self.assertEquals('tguard', flow.subject.guard)


    
class FlowItemActionTestCase(TestCase):
    """
    Flow item connecting to action item tests.
    """
    def test_glue(self):
        """Test flow item glueing to action items
        """
        flow = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        a2 = self.create(items.ActionItem, uml2.Action)

        glued = self.allow(flow, flow.head, a1)
        self.assertTrue(glued)

        self.connect(flow, flow.head, a1)

        glued = self.allow(flow, flow.tail, a2)
        self.assertTrue(glued)


    def test_connect(self):
        """Test flow item connecting to action items
        """
        flow = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        a2 = self.create(items.ActionItem, uml2.Action)

        self.connect(flow, flow.head, a1)
        self.connect(flow, flow.tail, a2)

        self.assertTrue(isinstance(flow.subject, uml2.ControlFlow))

        self.assertEquals(0, len(a1.subject.incoming))
        self.assertEquals(1, len(a2.subject.incoming))
        self.assertEquals(1, len(a1.subject.outgoing))
        self.assertEquals(0, len(a2.subject.outgoing))

        self.assertTrue(flow.subject in a1.subject.outgoing)
        self.assertTrue(flow.subject.source is a1.subject)
        self.assertTrue(flow.subject in a2.subject.incoming)
        self.assertTrue(flow.subject.target is a2.subject)


    def test_disconnect(self):
        """Test flow item disconnection from action items
        """
        flow = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        a2 = self.create(items.ActionItem, uml2.Action)

        self.connect(flow, flow.head, a1)
        self.connect(flow, flow.tail, a2)

        self.disconnect(flow, flow.head)
        self.assertTrue(flow.subject is None)
        self.assertEquals(0, len(a1.subject.incoming))
        self.assertEquals(0, len(a2.subject.incoming))
        self.assertEquals(0, len(a1.subject.outgoing))
        self.assertEquals(0, len(a2.subject.outgoing))


    def test_reconnect(self):
        """Test flow item reconnection
        """
        flow = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        a2 = self.create(items.ActionItem, uml2.Action)
        a3 = self.create(items.ActionItem, uml2.Action)

        # a1 -> a2
        self.connect(flow, flow.head, a1)
        self.connect(flow, flow.tail, a2)
        f = flow.subject
        f.name = 'tname'
        f.guard = 'tguard'

        # reconnect: a1 -> a3
        self.connect(flow, flow.tail, a3)

        self.assertEquals(0, len(a1.subject.incoming))
        self.assertEquals(1, len(a1.subject.outgoing))
        # no connections to a2
        self.assertEquals(0, len(a2.subject.incoming))
        self.assertEquals(0, len(a2.subject.outgoing))
        # connections to a3 instead
        self.assertEquals(1, len(a3.subject.incoming))
        self.assertEquals(0, len(a3.subject.outgoing))

        self.assertEquals(1, len(self.kindof(uml2.ControlFlow)))
        # one guard
        self.assertEquals('tname', flow.subject.name)
        self.assertEquals('tguard', flow.subject.guard)


    def test_object_flow_reconnection(self):
        """Test object flow becoming control flow due to reconnection
        """
        flow = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        a2 = self.create(items.ActionItem, uml2.Action)
        o1 = self.create(items.ObjectNodeItem, uml2.ObjectNode)

        # connect with control flow: a1 -> o1
        self.connect(flow, flow.head, a1)
        self.connect(flow, flow.tail, o1)

        f = flow.subject
        f.name = 'tname'
        f.guard = 'tguard'

        # reconnect with object flow: a1 -> a2
        self.connect(flow, flow.tail, a2)

        self.assertEquals(0, len(a1.subject.incoming))
        self.assertEquals(1, len(a1.subject.outgoing))
        # no connections to o1
        self.assertEquals(0, len(o1.subject.incoming))
        self.assertEquals(0, len(o1.subject.outgoing))
        # connections to a2 instead
        self.assertEquals(1, len(a2.subject.incoming))
        self.assertEquals(0, len(a2.subject.outgoing))

        self.assertEquals(1, len(self.kindof(uml2.ControlFlow)))
        self.assertEquals(0, len(self.kindof(uml2.ObjectFlow)))
        # one guard, not changed
        self.assertEquals('tname', flow.subject.name)
        self.assertEquals('tguard', flow.subject.guard)


class FlowItemDesisionAndForkNodes:
    """
    Base class for flow connecting to decision and fork nodes.
    
    See `FlowItemDecisionNodeTestCase` and `FlowItemForkNodeTestCase` test
    cases.

    Not tested yet

    - If a join node has an incoming object flow, it must have an outgoing
      object flow, otherwise, it must have an outgoing control flow.
    - The edges coming into and out of a fork node must be either all
      object flows or all control flows.
    """

    item_cls = None
    fork_node_cls = None
    join_node_cls = None

    def test_glue(self):
        """Test decision/fork nodes glue
        """
        flow = self.create(items.FlowItem)
        action = self.create(items.ActionItem, uml2.Action)
        node = self.create(self.item_cls, self.join_node_cls)

        glued = self.allow(flow, flow.head, node)
        self.assertTrue(glued)

        self.connect(flow, flow.head, action)

        glued = self.allow(flow, flow.tail, node)
        self.assertTrue(glued)


    def test_node_class_change(self):
        """ Test node incoming edges

        Connection scheme is presented below::

                  head  tail
            [ a1 ]--flow1-->    |
                             [ jn ] --flow3--> [ a3 ]
            [ a2 ]--flow2-->    |

        Node class changes due to two incoming edges and one outgoing edge.
        """
        flow1 = self.create(items.FlowItem)
        flow2 = self.create(items.FlowItem)
        flow3 = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        a2 = self.create(items.ActionItem, uml2.Action)
        a3 = self.create(items.ActionItem, uml2.Action)
        jn = self.create(self.item_cls, self.fork_node_cls)

        assert type(jn.subject) is self.fork_node_cls

        # connect actions first
        self.connect(flow1, flow1.head, a1)
        self.connect(flow2, flow2.head, a2)
        self.connect(flow3, flow3.tail, a2)

        # connect to the node
        self.connect(flow1, flow1.tail, jn)
        self.connect(flow2, flow2.tail, jn)
        self.connect(flow3, flow3.head, jn)

        # node class changes
        self.assertTrue(type(jn.subject) is self.join_node_cls)


    def test_outgoing_edges(self):
        """Test outgoing edges


        Connection scheme is presented below::

                   head  tail    | --flow2-->[ a2 ]
            [ a1 ] --flow1--> [ jn ]
                                 | --flow3-->[ a3 ]
        """
        flow1 = self.create(items.FlowItem)
        flow2 = self.create(items.FlowItem)
        flow3 = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        a2 = self.create(items.ActionItem, uml2.Action)
        a3 = self.create(items.ActionItem, uml2.Action)
        jn = self.create(self.item_cls, self.join_node_cls)

        # connect actions first
        self.connect(flow1, flow1.head, a1)
        self.connect(flow2, flow2.tail, a2)
        self.connect(flow3, flow3.tail, a2)

        # connect to the node
        self.connect(flow1, flow1.tail, jn)
        self.assertTrue(type(jn.subject) is self.join_node_cls)

        self.connect(flow2, flow2.head, jn)
        self.assertTrue(type(jn.subject) is self.join_node_cls)

        self.assertEquals(1, len(jn.subject.incoming))
        self.assertEquals(1, len(jn.subject.outgoing))
        self.assertTrue(flow1.subject in jn.subject.incoming)
        self.assertTrue(flow2.subject in jn.subject.outgoing)

        self.connect(flow3, flow3.head, jn)
        self.assertEquals(2, len(jn.subject.outgoing))

        self.assertTrue(type(jn.subject) is self.fork_node_cls,
                '%s' % jn.subject)


    def test_combined_nodes_connection(self):
        """Test combined nodes connection

        Connection scheme is presented below::

                   head  tail    |   --flow2--> [ a2 ]
            [ a1 ] --flow1--> [ jn ]
            [ a4 ] --flow4-->    |   --flow3--> [ a3 ]

        Flow `flow4` will force the node to become a combined node.
        """
        flow1 = self.create(items.FlowItem)
        flow2 = self.create(items.FlowItem)
        flow3 = self.create(items.FlowItem)
        flow4 = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        a2 = self.create(items.ActionItem, uml2.Action)
        a3 = self.create(items.ActionItem, uml2.Action)
        a4 = self.create(items.ActionItem, uml2.Action)
        jn = self.create(self.item_cls, self.join_node_cls)

        # connect actions first
        self.connect(flow1, flow1.head, a1)
        self.connect(flow2, flow2.tail, a2)
        self.connect(flow3, flow3.tail, a2)
        self.connect(flow4, flow4.head, a4)

        # connect to the node
        self.connect(flow1, flow1.tail, jn)
        self.connect(flow2, flow2.head, jn)
        self.connect(flow3, flow3.head, jn)

        self.connect(flow4, flow4.tail, jn)
        self.assertTrue(type(jn.subject) is self.join_node_cls)
        self.assertTrue(jn.combined is not None)

        # check node combination
        self.assertTrue(1, len(jn.subject.outgoing))
        self.assertTrue(1, len(jn.combined.incoming))
        self.assertTrue(jn.subject.outgoing[0] is jn.combined.incoming[0])


    def test_combined_node_disconnection(self):
        """Test combined nodes disconnection

        Connection scheme is presented below::

                   head  tail    |   --flow2--> [ a2 ]
            [ a1 ] --flow1--> [ jn ]
            [ a4 ] --flow4-->    |   --flow3--> [ a3 ]

        Flow `flow4` will force the node to become a combined node.
        """
        canvas = self.diagram.canvas

        flow1 = self.create(items.FlowItem)
        flow2 = self.create(items.FlowItem)
        flow3 = self.create(items.FlowItem)
        flow4 = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, uml2.Action)
        a2 = self.create(items.ActionItem, uml2.Action)
        a3 = self.create(items.ActionItem, uml2.Action)
        a4 = self.create(items.ActionItem, uml2.Action)
        jn = self.create(self.item_cls, self.join_node_cls)

        # connect actions first
        self.connect(flow1, flow1.head, a1)
        self.connect(flow2, flow2.tail, a2)
        self.connect(flow3, flow3.tail, a2)
        self.connect(flow4, flow4.head, a4)

        # connect to the node
        self.connect(flow1, flow1.tail, jn)
        self.connect(flow2, flow2.head, jn)
        self.connect(flow3, flow3.head, jn)
        self.connect(flow4, flow4.tail, jn)

        # needed for tests below
        cflow = jn.subject.outgoing[0]
        cnode = jn.combined
        assert cflow in self.kindof(uml2.ControlFlow)
        assert cnode in self.kindof(self.fork_node_cls)

        # test disconnection
        self.disconnect(flow4, flow4.head)
        assert self.get_connected(flow4.head) is None
        self.assertTrue(jn.combined is None)

        flows = self.kindof(uml2.ControlFlow)
        nodes = self.kindof(self.fork_node_cls)
        self.assertTrue(cnode not in nodes, '%s in %s' % (cnode, nodes))
        self.assertTrue(cflow not in flows, '%s in %s' % (cflow, flows))



class FlowItemForkNodeTestCase(FlowItemDesisionAndForkNodes, TestCase):
    item_cls = items.ForkNodeItem
    fork_node_cls = uml2.ForkNode
    join_node_cls = uml2.JoinNode



class FlowItemDecisionNodeTestCase(FlowItemDesisionAndForkNodes, TestCase):
    item_cls = items.DecisionNodeItem
    fork_node_cls = uml2.DecisionNode
    join_node_cls = uml2.MergeNode



# vim:sw=4:et:ai
