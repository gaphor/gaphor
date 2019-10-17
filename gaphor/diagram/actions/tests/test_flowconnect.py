"""
Flow item connection adapters tests.
"""

from typing import Type
from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram.actions.action import ActionItem
from gaphor.diagram.actions.flow import FlowItem
from gaphor.diagram.actions.activitynodes import (
    InitialNodeItem,
    ForkNodeItem,
    FlowFinalNodeItem,
    ActivityFinalNodeItem,
    ActivityNodeItem,
    DecisionNodeItem,
)
from gaphor.diagram.actions.objectnode import ObjectNodeItem


class FlowItemBasicNodesConnectionTestCase(TestCase):
    """
    Tests for flow item connecting to basic activity nodes.
    """

    def test_initial_node_glue(self):
        """Test flow item gluing to initial node item."""

        flow = self.create(FlowItem)
        node = self.create(InitialNodeItem, UML.InitialNode)

        # tail may not connect to initial node item
        allowed = self.allow(flow, flow.tail, node)
        assert not allowed

        allowed = self.allow(flow, flow.head, node)
        assert allowed

    def test_flow_final_node_glue(self):
        """Test flow item gluing to flow final node item."""

        flow = self.create(FlowItem)
        node = self.create(FlowFinalNodeItem, UML.FlowFinalNode)

        # head may not connect to flow final node item
        allowed = self.allow(flow, flow.head, node)
        assert not allowed

        allowed = self.allow(flow, flow.tail, node)
        assert allowed

    def test_activity_final_node_glue(self):
        """Test flow item gluing to activity final node item
        """
        flow = self.create(FlowItem)
        node = self.create(ActivityFinalNodeItem, UML.ActivityFinalNode)

        # head may not connect to activity final node item
        glued = self.allow(flow, flow.head, node)
        assert not glued

        glued = self.allow(flow, flow.tail, node)
        assert glued


class FlowItemObjectNodeTestCase(TestCase):
    """
    Flow item connecting to object node item tests.
    """

    def test_glue_to_object_node(self):
        flow = self.create(FlowItem)
        onode = self.create(ObjectNodeItem, UML.ObjectNode)
        glued = self.allow(flow, flow.head, onode)
        assert glued

    def test_connect_to_object_node(self):
        flow = self.create(FlowItem)
        anode = self.create(ActionItem, UML.Action)
        onode = self.create(ObjectNodeItem, UML.ObjectNode)

        self.connect(flow, flow.head, anode)
        self.connect(flow, flow.tail, onode)
        assert flow.subject
        assert isinstance(flow.subject, UML.ObjectFlow)

        self.disconnect(flow, flow.head)
        self.disconnect(flow, flow.tail)

        # opposite connection
        self.connect(flow, flow.head, onode)
        self.connect(flow, flow.tail, anode)
        assert flow.subject
        assert isinstance(flow.subject, UML.ObjectFlow)

    def test_object_flow_reconnect(self):
        flow = self.create(FlowItem)
        a1 = self.create(ActionItem, UML.Action)
        o1 = self.create(ObjectNodeItem, UML.ObjectNode)
        o2 = self.create(ObjectNodeItem, UML.ObjectNode)

        # connect: a1 -> o1
        self.connect(flow, flow.head, a1)
        self.connect(flow, flow.tail, o1)

        f = flow.subject
        f.name = "tname"
        f.guard = "tguard"

        # reconnect: a1 -> o2
        self.connect(flow, flow.tail, o2)

        assert 0 == len(a1.subject.incoming)
        assert 1 == len(a1.subject.outgoing)
        # no connections to o1
        self.assertEqual(0, len(o1.subject.incoming))
        assert 0 == len(o1.subject.outgoing)
        # connections to o2 instead
        self.assertEqual(1, len(o2.subject.incoming))
        assert 0 == len(o2.subject.outgoing)

        assert 1 == len(self.kindof(UML.ObjectFlow))
        # one guard
        self.assertEqual("tname", flow.subject.name)
        assert "tguard" == flow.subject.guard

    def test_control_flow_reconnection(self):
        """Test control flow becoming object flow due to reconnection
        """
        flow = self.create(FlowItem)
        a1 = self.create(ActionItem, UML.Action)
        a2 = self.create(ActionItem, UML.Action)
        o1 = self.create(ObjectNodeItem, UML.ObjectNode)

        # connect with control flow: a1 -> a2
        self.connect(flow, flow.head, a1)
        self.connect(flow, flow.tail, a2)

        f = flow.subject
        f.name = "tname"
        f.guard = "tguard"

        # reconnect with object flow: a1 -> o1
        self.connect(flow, flow.tail, o1)

        assert 0 == len(a1.subject.incoming)
        assert 1 == len(a1.subject.outgoing)
        # no connections to a2
        self.assertEqual(0, len(a2.subject.incoming))
        assert 0 == len(a2.subject.outgoing)
        # connections to o1 instead
        self.assertEqual(1, len(o1.subject.incoming))
        assert 0 == len(o1.subject.outgoing)

        assert 0 == len(self.kindof(UML.ControlFlow))
        assert 1 == len(self.kindof(UML.ObjectFlow))
        # one guard, not changed
        self.assertEqual("tname", flow.subject.name)
        assert "tguard" == flow.subject.guard


class FlowItemActionTestCase(TestCase):
    """
    Flow item connecting to action item tests.
    """

    def test_glue(self):
        """Test flow item gluing to action items."""

        flow = self.create(FlowItem)
        a1 = self.create(ActionItem, UML.Action)
        a2 = self.create(ActionItem, UML.Action)

        glued = self.allow(flow, flow.head, a1)
        assert glued

        self.connect(flow, flow.head, a1)

        glued = self.allow(flow, flow.tail, a2)
        assert glued

    def test_connect_to_action_item(self):
        flow = self.create(FlowItem)
        a1 = self.create(ActionItem, UML.Action)
        a2 = self.create(ActionItem, UML.Action)

        self.connect(flow, flow.head, a1)
        self.connect(flow, flow.tail, a2)

        assert isinstance(flow.subject, UML.ControlFlow)

        assert 0 == len(a1.subject.incoming)
        assert 1 == len(a2.subject.incoming)
        assert 1 == len(a1.subject.outgoing)
        assert 0 == len(a2.subject.outgoing)

        assert flow.subject in a1.subject.outgoing
        assert flow.subject.source is a1.subject
        assert flow.subject in a2.subject.incoming
        assert flow.subject.target is a2.subject

    def test_disconnect_from_action_item(self):
        """Test flow item disconnection from action items
        """
        flow = self.create(FlowItem)
        a1 = self.create(ActionItem, UML.Action)
        a2 = self.create(ActionItem, UML.Action)

        self.connect(flow, flow.head, a1)
        self.connect(flow, flow.tail, a2)

        self.disconnect(flow, flow.head)
        assert flow.subject is None
        assert 0 == len(a1.subject.incoming)
        assert 0 == len(a2.subject.incoming)
        assert 0 == len(a1.subject.outgoing)
        assert 0 == len(a2.subject.outgoing)

    def test_reconnect(self):
        """Test flow item reconnection
        """
        flow = self.create(FlowItem)
        a1 = self.create(ActionItem, UML.Action)
        a2 = self.create(ActionItem, UML.Action)
        a3 = self.create(ActionItem, UML.Action)

        # a1 -> a2
        self.connect(flow, flow.head, a1)
        self.connect(flow, flow.tail, a2)
        f = flow.subject
        f.name = "tname"
        f.guard = "tguard"

        # reconnect: a1 -> a3
        self.connect(flow, flow.tail, a3)

        assert 0 == len(a1.subject.incoming)
        assert 1 == len(a1.subject.outgoing)
        # no connections to a2
        self.assertEqual(0, len(a2.subject.incoming))
        assert 0 == len(a2.subject.outgoing)
        # connections to a3 instead
        self.assertEqual(1, len(a3.subject.incoming))
        assert 0 == len(a3.subject.outgoing)

        assert 1 == len(self.kindof(UML.ControlFlow))
        # one guard
        self.assertEqual("tname", flow.subject.name)
        assert "tguard" == flow.subject.guard

    def test_object_flow_reconnection(self):
        """Test object flow becoming control flow due to reconnection
        """
        flow = self.create(FlowItem)
        a1 = self.create(ActionItem, UML.Action)
        a2 = self.create(ActionItem, UML.Action)
        o1 = self.create(ObjectNodeItem, UML.ObjectNode)

        # connect with control flow: a1 -> o1
        self.connect(flow, flow.head, a1)
        self.connect(flow, flow.tail, o1)

        f = flow.subject
        f.name = "tname"
        f.guard = "tguard"

        # reconnect with object flow: a1 -> a2
        self.connect(flow, flow.tail, a2)

        assert 0 == len(a1.subject.incoming)
        assert 1 == len(a1.subject.outgoing)
        # no connections to o1
        self.assertEqual(0, len(o1.subject.incoming))
        assert 0 == len(o1.subject.outgoing)
        # connections to a2 instead
        self.assertEqual(1, len(a2.subject.incoming))
        assert 0 == len(a2.subject.outgoing)

        assert 1 == len(self.kindof(UML.ControlFlow))
        assert 0 == len(self.kindof(UML.ObjectFlow))
        # one guard, not changed
        self.assertEqual("tname", flow.subject.name)
        assert "tguard" == flow.subject.guard


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

    item_cls: Type[UML.Presentation]
    fork_node_cls: Type[UML.ControlNode]
    join_node_cls: Type[UML.ControlNode]

    def test_glue(self):
        """Test decision/fork nodes glue
        """
        flow = self.create(FlowItem)
        action = self.create(ActionItem, UML.Action)
        node = self.create(self.item_cls, self.join_node_cls)

        glued = self.allow(flow, flow.head, node)
        assert glued

        self.connect(flow, flow.head, action)

        glued = self.allow(flow, flow.tail, node)
        assert glued

    def test_node_class_change(self):
        """ Test node incoming edges

        Connection scheme is presented below::

                  head  tail
            [ a1 ]--flow1-->    |
                             [ jn ] --flow3--> [ a3 ]
            [ a2 ]--flow2-->    |

        Node class changes due to two incoming edges and one outgoing edge.
        """
        flow1 = self.create(FlowItem)
        flow2 = self.create(FlowItem)
        flow3 = self.create(FlowItem)
        a1 = self.create(ActionItem, UML.Action)
        a2 = self.create(ActionItem, UML.Action)
        a3 = self.create(ActionItem, UML.Action)
        jn = self.create(self.item_cls, self.fork_node_cls)

        assert isinstance(jn.subject, self.fork_node_cls)

        # connect actions first
        self.connect(flow1, flow1.head, a1)
        self.connect(flow2, flow2.head, a2)
        self.connect(flow3, flow3.tail, a2)

        # connect to the node
        self.connect(flow1, flow1.tail, jn)
        self.connect(flow2, flow2.tail, jn)
        self.connect(flow3, flow3.head, jn)

        # node class changes
        self.assertTrue(isinstance(jn.subject, self.join_node_cls))

    def test_outgoing_edges(self):
        """Test outgoing edges


        Connection scheme is presented below::

                   head  tail    | --flow2-->[ a2 ]
            [ a1 ] --flow1--> [ jn ]
                                 | --flow3-->[ a3 ]
        """
        flow1 = self.create(FlowItem)
        flow2 = self.create(FlowItem)
        flow3 = self.create(FlowItem)
        a1 = self.create(ActionItem, UML.Action)
        a2 = self.create(ActionItem, UML.Action)
        a3 = self.create(ActionItem, UML.Action)
        jn = self.create(self.item_cls, self.join_node_cls)

        # connect actions first
        self.connect(flow1, flow1.head, a1)
        self.connect(flow2, flow2.tail, a2)
        self.connect(flow3, flow3.tail, a2)

        # connect to the node
        self.connect(flow1, flow1.tail, jn)
        assert isinstance(jn.subject, self.join_node_cls)

        self.connect(flow2, flow2.head, jn)
        assert isinstance(jn.subject, self.join_node_cls)

        assert 1 == len(jn.subject.incoming)
        assert 1 == len(jn.subject.outgoing)
        assert flow1.subject in jn.subject.incoming
        assert flow2.subject in jn.subject.outgoing

        self.connect(flow3, flow3.head, jn)
        assert 2 == len(jn.subject.outgoing)

        assert isinstance(jn.subject, self.fork_node_cls), f"{jn.subject}"

    def test_combined_nodes_connection(self):
        """Test combined nodes connection

        Connection scheme is presented below::

                   head  tail    |   --flow2--> [ a2 ]
            [ a1 ] --flow1--> [ jn ]
            [ a4 ] --flow4-->    |   --flow3--> [ a3 ]

        Flow `flow4` will force the node to become a combined node.
        """
        flow1 = self.create(FlowItem)
        flow2 = self.create(FlowItem)
        flow3 = self.create(FlowItem)
        flow4 = self.create(FlowItem)
        a1 = self.create(ActionItem, UML.Action)
        a2 = self.create(ActionItem, UML.Action)
        a3 = self.create(ActionItem, UML.Action)
        a4 = self.create(ActionItem, UML.Action)
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
        assert isinstance(jn.subject, self.join_node_cls)
        assert jn.combined is not None

        # check node combination
        self.assertTrue(1, len(jn.subject.outgoing))
        assert 1, len(jn.combined.incoming)
        assert jn.subject.outgoing[0] is jn.combined.incoming[0]

    def test_combined_node_disconnection(self):
        """Test combined nodes disconnection

        Connection scheme is presented below::

                   head  tail    |   --flow2--> [ a2 ]
            [ a1 ] --flow1--> [ jn ]
            [ a4 ] --flow4-->    |   --flow3--> [ a3 ]

        Flow `flow4` will force the node to become a combined node.
        """
        canvas = self.diagram.canvas

        flow1 = self.create(FlowItem)
        flow2 = self.create(FlowItem)
        flow3 = self.create(FlowItem)
        flow4 = self.create(FlowItem)
        a1 = self.create(ActionItem, UML.Action)
        a2 = self.create(ActionItem, UML.Action)
        a3 = self.create(ActionItem, UML.Action)
        a4 = self.create(ActionItem, UML.Action)
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
        assert cflow in self.kindof(UML.ControlFlow)
        assert cnode in self.kindof(self.fork_node_cls)

        # test disconnection
        self.disconnect(flow4, flow4.head)
        assert self.get_connected(flow4.head) is None
        assert jn.combined is None

        flows = self.kindof(UML.ControlFlow)
        nodes = self.kindof(self.fork_node_cls)
        assert cnode not in nodes, f"{cnode} in {nodes}"
        assert cflow not in flows, f"{cflow} in {flows}"


class FlowItemForkNodeTestCase(FlowItemDesisionAndForkNodes, TestCase):
    item_cls = ForkNodeItem
    fork_node_cls = UML.ForkNode
    join_node_cls = UML.JoinNode


class FlowItemDecisionNodeTestCase(FlowItemDesisionAndForkNodes, TestCase):
    item_cls = DecisionNodeItem
    fork_node_cls = UML.DecisionNode
    join_node_cls = UML.MergeNode
