"""Flow item connection adapters tests."""

from typing import Type

from gaphor import UML
from gaphor.core.modeling import Presentation
from gaphor.UML.actions.action import ActionItem
from gaphor.UML.actions.activitynodes import (
    ActivityFinalNodeItem,
    DecisionNodeItem,
    FlowFinalNodeItem,
    ForkNodeItem,
    InitialNodeItem,
)
from gaphor.UML.actions.flow import FlowItem
from gaphor.UML.actions.objectnode import ObjectNodeItem


class TestFlowItemBasicNodesConnection:
    """Tests for flow item connecting to basic activity nodes."""

    def test_initial_node_glue(self, case):
        """Test flow item gluing to initial node item."""

        flow = case.create(FlowItem)
        node = case.create(InitialNodeItem, UML.InitialNode)

        # tail may not connect to initial node item
        allowed = case.allow(flow, flow.tail, node)
        assert not allowed

        allowed = case.allow(flow, flow.head, node)
        assert allowed

    def test_flow_final_node_glue(self, case):
        """Test flow item gluing to flow final node item."""

        flow = case.create(FlowItem)
        node = case.create(FlowFinalNodeItem, UML.FlowFinalNode)

        # head may not connect to flow final node item
        allowed = case.allow(flow, flow.head, node)
        assert not allowed

        allowed = case.allow(flow, flow.tail, node)
        assert allowed

    def test_activity_final_node_glue(self, case):
        """Test flow item gluing to activity final node item."""
        flow = case.create(FlowItem)
        node = case.create(ActivityFinalNodeItem, UML.ActivityFinalNode)

        # head may not connect to activity final node item
        glued = case.allow(flow, flow.head, node)
        assert not glued

        glued = case.allow(flow, flow.tail, node)
        assert glued


class TestFlowItemObjectNode:
    """Flow item connecting to object node item tests."""

    def test_glue_to_object_node(self, case):
        flow = case.create(FlowItem)
        onode = case.create(ObjectNodeItem, UML.ObjectNode)
        glued = case.allow(flow, flow.head, onode)
        assert glued

    def test_connect_to_object_node(self, case):
        flow = case.create(FlowItem)
        anode = case.create(ActionItem, UML.Action)
        onode = case.create(ObjectNodeItem, UML.ObjectNode)

        case.connect(flow, flow.head, anode)
        case.connect(flow, flow.tail, onode)
        assert flow.subject
        assert isinstance(flow.subject, UML.ObjectFlow)

        case.disconnect(flow, flow.head)
        case.disconnect(flow, flow.tail)

        # opposite connection
        case.connect(flow, flow.head, onode)
        case.connect(flow, flow.tail, anode)
        assert flow.subject
        assert isinstance(flow.subject, UML.ObjectFlow)

    def test_object_flow_reconnect(self, case):
        flow = case.create(FlowItem)
        a1 = case.create(ActionItem, UML.Action)
        o1 = case.create(ObjectNodeItem, UML.ObjectNode)
        o2 = case.create(ObjectNodeItem, UML.ObjectNode)

        # connect: a1 -> o1
        case.connect(flow, flow.head, a1)
        case.connect(flow, flow.tail, o1)

        f = flow.subject
        f.name = "tname"
        f.guard = "tguard"

        # reconnect: a1 -> o2
        case.connect(flow, flow.tail, o2)

        assert len(a1.subject.incoming) == 0
        assert len(a1.subject.outgoing) == 1
        # no connections to o1
        assert len(o1.subject.incoming) == 0
        assert len(o1.subject.outgoing) == 0
        # connections to o2 instead
        assert len(o2.subject.incoming) == 1
        assert len(o2.subject.outgoing) == 0

        assert len(case.kindof(UML.ObjectFlow)) == 1
        # one guard
        assert flow.subject.name == "tname"
        assert flow.subject.guard == "tguard"

    def test_control_flow_reconnection(self, case):
        """Test control flow becoming object flow due to reconnection."""
        flow = case.create(FlowItem)
        a1 = case.create(ActionItem, UML.Action)
        a2 = case.create(ActionItem, UML.Action)
        o1 = case.create(ObjectNodeItem, UML.ObjectNode)

        # connect with control flow: a1 -> a2
        case.connect(flow, flow.head, a1)
        case.connect(flow, flow.tail, a2)

        f = flow.subject
        f.name = "tname"
        f.guard = "tguard"

        # reconnect with object flow: a1 -> o1
        case.connect(flow, flow.tail, o1)

        assert len(a1.subject.incoming) == 0
        assert len(a1.subject.outgoing) == 1
        # no connections to a2
        assert len(a2.subject.incoming) == 0
        assert len(a2.subject.outgoing) == 0
        # connections to o1 instead
        assert len(o1.subject.incoming) == 1
        assert len(o1.subject.outgoing) == 0

        assert len(case.kindof(UML.ControlFlow)) == 0
        assert len(case.kindof(UML.ObjectFlow)) == 1
        # one guard, not changed
        assert flow.subject.name == "tname"
        assert flow.subject.guard == "tguard"


class TestFlowItemAction:
    """Flow item connecting to action item tests."""

    def test_glue(self, case):
        """Test flow item gluing to action items."""

        flow = case.create(FlowItem)
        a1 = case.create(ActionItem, UML.Action)
        a2 = case.create(ActionItem, UML.Action)

        glued = case.allow(flow, flow.head, a1)
        assert glued

        case.connect(flow, flow.head, a1)

        glued = case.allow(flow, flow.tail, a2)
        assert glued

    def test_connect_to_action_item(self, case):
        flow = case.create(FlowItem)
        a1 = case.create(ActionItem, UML.Action)
        a2 = case.create(ActionItem, UML.Action)

        case.connect(flow, flow.head, a1)
        case.connect(flow, flow.tail, a2)

        assert isinstance(flow.subject, UML.ControlFlow)

        assert len(a1.subject.incoming) == 0
        assert len(a2.subject.incoming) == 1
        assert len(a1.subject.outgoing) == 1
        assert len(a2.subject.outgoing) == 0

        assert flow.subject in a1.subject.outgoing
        assert flow.subject.source is a1.subject
        assert flow.subject in a2.subject.incoming
        assert flow.subject.target is a2.subject

    def test_disconnect_from_action_item(self, case):
        """Test flow item disconnection from action items."""
        flow = case.create(FlowItem)
        a1 = case.create(ActionItem, UML.Action)
        a2 = case.create(ActionItem, UML.Action)

        case.connect(flow, flow.head, a1)
        case.connect(flow, flow.tail, a2)

        case.disconnect(flow, flow.head)
        assert flow.subject is None
        assert len(a1.subject.incoming) == 0
        assert len(a2.subject.incoming) == 0
        assert len(a1.subject.outgoing) == 0
        assert len(a2.subject.outgoing) == 0

    def test_reconnect(self, case):
        """Test flow item reconnection."""
        flow = case.create(FlowItem)
        a1 = case.create(ActionItem, UML.Action)
        a2 = case.create(ActionItem, UML.Action)
        a3 = case.create(ActionItem, UML.Action)

        # a1 -> a2
        case.connect(flow, flow.head, a1)
        case.connect(flow, flow.tail, a2)
        f = flow.subject
        f.name = "tname"
        f.guard = "tguard"

        # reconnect: a1 -> a3
        case.connect(flow, flow.tail, a3)

        assert len(a1.subject.incoming) == 0
        assert len(a1.subject.outgoing) == 1
        # no connections to a2
        assert len(a2.subject.incoming) == 0
        assert len(a2.subject.outgoing) == 0
        # connections to a3 instead
        assert len(a3.subject.incoming) == 1
        assert len(a3.subject.outgoing) == 0

        assert len(case.kindof(UML.ControlFlow)) == 1
        # one guard
        assert flow.subject.name == "tname"
        assert flow.subject.guard == "tguard"

    def test_object_flow_reconnection(self, case):
        """Test object flow becoming control flow due to reconnection."""
        flow = case.create(FlowItem)
        a1 = case.create(ActionItem, UML.Action)
        a2 = case.create(ActionItem, UML.Action)
        o1 = case.create(ObjectNodeItem, UML.ObjectNode)

        # connect with control flow: a1 -> o1
        case.connect(flow, flow.head, a1)
        case.connect(flow, flow.tail, o1)

        f = flow.subject
        f.name = "tname"
        f.guard = "tguard"

        # reconnect with object flow: a1 -> a2
        case.connect(flow, flow.tail, a2)

        assert len(a1.subject.incoming) == 0
        assert len(a1.subject.outgoing) == 1
        # no connections to o1
        assert len(o1.subject.incoming) == 0
        assert len(o1.subject.outgoing) == 0
        # connections to a2 instead
        assert len(a2.subject.incoming) == 1
        assert len(a2.subject.outgoing) == 0

        assert len(case.kindof(UML.ControlFlow)) == 1
        assert len(case.kindof(UML.ObjectFlow)) == 0
        # one guard, not changed
        assert flow.subject.name == "tname"
        assert flow.subject.guard == "tguard"


class FlowItemDecisionAndForkNodes:
    """Base class for flow connecting to decision and fork nodes.

    See `TestFlowItemDecisionNode` and `Test FlowItemForkNode` test cases.

    Not tested yet

    - If a join node has an incoming object flow, it must have an outgoing
      object flow, otherwise, it must have an outgoing control flow.
    - The edges coming into and out of a fork node must be either all
      object flows or all control flows.
    """

    item_cls: Type[Presentation]
    fork_node_cls: Type[UML.ControlNode]
    join_node_cls: Type[UML.ControlNode]

    def test_glue(self, case):
        """Test decision/fork nodes glue."""
        flow = case.create(FlowItem)
        action = case.create(ActionItem, UML.Action)
        node = case.create(self.item_cls, self.join_node_cls)

        glued = case.allow(flow, flow.head, node)
        assert glued

        case.connect(flow, flow.head, action)

        glued = case.allow(flow, flow.tail, node)
        assert glued

    def test_node_class_change(self, case):
        """Test node incoming edges.

        Connection scheme is presented below::

                  head  tail
            [ a1 ]--flow1-->    |
                             [ jn ] --flow3--> [ a3 ]
            [ a2 ]--flow2-->    |

        Node class changes due to two incoming edges and one outgoing edge.
        """
        flow1 = case.create(FlowItem)
        flow2 = case.create(FlowItem)
        flow3 = case.create(FlowItem)
        a1 = case.create(ActionItem, UML.Action)
        a2 = case.create(ActionItem, UML.Action)
        jn = case.create(self.item_cls, self.fork_node_cls)

        assert isinstance(jn.subject, self.fork_node_cls)

        # connect actions first
        case.connect(flow1, flow1.head, a1)
        case.connect(flow2, flow2.head, a2)
        case.connect(flow3, flow3.tail, a2)

        # connect to the node
        case.connect(flow1, flow1.tail, jn)
        case.connect(flow2, flow2.tail, jn)
        case.connect(flow3, flow3.head, jn)

        # node class changes
        assert isinstance(jn.subject, self.join_node_cls)

    def test_outgoing_edges(self, case):
        """Test outgoing edges.

        Connection scheme is presented below::

                   head  tail    | --flow2-->[ a2 ]
            [ a1 ] --flow1--> [ jn ]
                                 | --flow3-->[ a3 ]
        """
        flow1 = case.create(FlowItem)
        flow2 = case.create(FlowItem)
        flow3 = case.create(FlowItem)
        a1 = case.create(ActionItem, UML.Action)
        a2 = case.create(ActionItem, UML.Action)
        jn = case.create(self.item_cls, self.join_node_cls)

        # connect actions first
        case.connect(flow1, flow1.head, a1)
        case.connect(flow2, flow2.tail, a2)
        case.connect(flow3, flow3.tail, a2)

        # connect to the node
        case.connect(flow1, flow1.tail, jn)
        assert isinstance(jn.subject, self.join_node_cls)

        case.connect(flow2, flow2.head, jn)
        assert isinstance(jn.subject, self.join_node_cls)

        assert len(jn.subject.incoming) == 1
        assert len(jn.subject.outgoing) == 1
        assert flow1.subject in jn.subject.incoming
        assert flow2.subject in jn.subject.outgoing

        case.connect(flow3, flow3.head, jn)
        assert len(jn.subject.outgoing) == 2

        assert isinstance(jn.subject, self.fork_node_cls), f"{jn.subject}"

    def test_combined_nodes_connection(self, case):
        """Test combined nodes connection.

        Connection scheme is presented below::

                   head  tail    |   --flow2--> [ a2 ]
            [ a1 ] --flow1--> [ jn ]
            [ a4 ] --flow4-->    |   --flow3--> [ a3 ]

        Flow `flow4` will force the node to become a combined node.
        """
        flow1 = case.create(FlowItem)
        flow2 = case.create(FlowItem)
        flow3 = case.create(FlowItem)
        flow4 = case.create(FlowItem)
        a1 = case.create(ActionItem, UML.Action)
        a2 = case.create(ActionItem, UML.Action)
        a4 = case.create(ActionItem, UML.Action)
        jn = case.create(self.item_cls, self.join_node_cls)

        # connect actions first
        case.connect(flow1, flow1.head, a1)
        case.connect(flow2, flow2.tail, a2)
        case.connect(flow3, flow3.tail, a2)
        case.connect(flow4, flow4.head, a4)

        # connect to the node
        case.connect(flow1, flow1.tail, jn)
        case.connect(flow2, flow2.head, jn)
        case.connect(flow3, flow3.head, jn)

        case.connect(flow4, flow4.tail, jn)
        assert isinstance(jn.subject, self.join_node_cls)
        assert jn.combined is not None

        # check node combination
        assert len(jn.subject.outgoing) == 1
        assert len(jn.combined.incoming) == 1
        assert jn.subject.outgoing[0] is jn.combined.incoming[0]

    def test_combined_node_disconnection(self, case):
        """Test combined nodes disconnection.

        Connection scheme is presented below::

                   head  tail    |   --flow2--> [ a2 ]
            [ a1 ] --flow1--> [ jn ]
            [ a4 ] --flow4-->    |   --flow3--> [ a3 ]

        Flow `flow4` will force the node to become a combined node.
        """
        flow1 = case.create(FlowItem)
        flow2 = case.create(FlowItem)
        flow3 = case.create(FlowItem)
        flow4 = case.create(FlowItem)
        a1 = case.create(ActionItem, UML.Action)
        a2 = case.create(ActionItem, UML.Action)
        a4 = case.create(ActionItem, UML.Action)
        jn = case.create(self.item_cls, self.join_node_cls)

        # connect actions first
        case.connect(flow1, flow1.head, a1)
        case.connect(flow2, flow2.tail, a2)
        case.connect(flow3, flow3.tail, a2)
        case.connect(flow4, flow4.head, a4)

        # connect to the node
        case.connect(flow1, flow1.tail, jn)
        case.connect(flow2, flow2.head, jn)
        case.connect(flow3, flow3.head, jn)
        case.connect(flow4, flow4.tail, jn)

        # needed for tests below
        cflow = jn.subject.outgoing[0]
        cnode = jn.combined
        assert cflow in case.kindof(UML.ControlFlow)
        assert cnode in case.kindof(self.fork_node_cls)

        # test disconnection
        case.disconnect(flow4, flow4.head)
        assert case.get_connected(flow4.head) is None
        assert jn.combined is None

        flows = case.kindof(UML.ControlFlow)
        nodes = case.kindof(self.fork_node_cls)
        assert cnode not in nodes, f"{cnode} in {nodes}"
        assert cflow not in flows, f"{cflow} in {flows}"


class TestFlowItemForkNode(FlowItemDecisionAndForkNodes):
    item_cls = ForkNodeItem
    fork_node_cls = UML.ForkNode
    join_node_cls = UML.JoinNode


class TestFlowItemDecisionNode(FlowItemDecisionAndForkNodes):
    item_cls = DecisionNodeItem
    fork_node_cls = UML.DecisionNode
    join_node_cls = UML.MergeNode
