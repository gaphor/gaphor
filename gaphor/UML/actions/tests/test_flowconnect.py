"""Flow item connection adapters tests."""

from typing import Type

from gaphor import UML
from gaphor.core.modeling import Presentation
from gaphor.diagram.tests.fixtures import allow, connect, disconnect, get_connected
from gaphor.UML.actions.action import ActionItem
from gaphor.UML.actions.activitynodes import (
    ActivityFinalNodeItem,
    DecisionNodeItem,
    FlowFinalNodeItem,
    ForkNodeItem,
    InitialNodeItem,
)
from gaphor.UML.actions.flow import ControlFlowItem, ObjectFlowItem
from gaphor.UML.actions.objectnode import ObjectNodeItem


def test_initial_node_glue(create):
    """Test flow item gluing to initial node item."""

    flow = create(ControlFlowItem)
    node = create(InitialNodeItem, UML.InitialNode)

    # tail may not connect to initial node item
    allowed = allow(flow, flow.tail, node)
    assert not allowed

    allowed = allow(flow, flow.head, node)
    assert allowed


def test_flow_final_node_glue(create):
    """Test flow item gluing to flow final node item."""

    flow = create(ControlFlowItem)
    node = create(FlowFinalNodeItem, UML.FlowFinalNode)

    # head may not connect to flow final node item
    allowed = allow(flow, flow.head, node)
    assert not allowed

    allowed = allow(flow, flow.tail, node)
    assert allowed


def test_activity_final_node_glue(create):
    """Test flow item gluing to activity final node item."""
    flow = create(ControlFlowItem)
    node = create(ActivityFinalNodeItem, UML.ActivityFinalNode)

    # head may not connect to activity final node item
    glued = allow(flow, flow.head, node)
    assert not glued

    glued = allow(flow, flow.tail, node)
    assert glued


def test_glue_to_object_node(create):
    flow = create(ObjectFlowItem)
    onode = create(ObjectNodeItem, UML.ObjectNode)
    glued = allow(flow, flow.head, onode)
    assert glued


def test_connect_to_object_node(create):
    flow = create(ObjectFlowItem)
    anode = create(ActionItem, UML.Action)
    onode = create(ObjectNodeItem, UML.ObjectNode)

    connect(flow, flow.head, anode)
    connect(flow, flow.tail, onode)
    assert flow.subject
    assert isinstance(flow.subject, UML.ObjectFlow)

    disconnect(flow, flow.head)
    disconnect(flow, flow.tail)

    # opposite connection
    connect(flow, flow.head, onode)
    connect(flow, flow.tail, anode)
    assert flow.subject
    assert isinstance(flow.subject, UML.ObjectFlow)


def test_object_flow_reconnect(create, element_factory):
    flow = create(ObjectFlowItem)
    a1 = create(ActionItem, UML.Action)
    o1 = create(ObjectNodeItem, UML.ObjectNode)
    o2 = create(ObjectNodeItem, UML.ObjectNode)

    # connect: a1 -> o1
    connect(flow, flow.head, a1)
    connect(flow, flow.tail, o1)

    f = flow.subject
    f.name = "tname"
    f.guard = "tguard"

    # reconnect: a1 -> o2
    connect(flow, flow.tail, o2)

    assert len(a1.subject.incoming) == 0
    assert len(a1.subject.outgoing) == 1
    # no connections to o1
    assert len(o1.subject.incoming) == 0
    assert len(o1.subject.outgoing) == 0
    # connections to o2 instead
    assert len(o2.subject.incoming) == 1
    assert len(o2.subject.outgoing) == 0

    assert len(element_factory.lselect(UML.ObjectFlow)) == 1
    # one guard
    assert flow.subject.name == "tname"
    assert flow.subject.guard == "tguard"


def test_control_flow_reconnection(create):
    """Test control flow becoming object flow due to reconnection."""
    flow = create(ControlFlowItem)
    a1 = create(ActionItem, UML.Action)
    a2 = create(ActionItem, UML.Action)
    a3 = create(ActionItem, UML.Action)

    # connect with control flow: a1 -> a2
    connect(flow, flow.head, a1)
    connect(flow, flow.tail, a2)

    f = flow.subject
    f.name = "tname"
    f.guard = "tguard"

    # reconnect with object flow: a1 -> o1
    connect(flow, flow.tail, a3)

    assert len(a1.subject.incoming) == 0
    assert len(a1.subject.outgoing) == 1
    # no connections to a2
    assert len(a2.subject.incoming) == 0
    assert len(a2.subject.outgoing) == 0
    # connections to o1 instead
    assert len(a3.subject.incoming) == 1
    assert len(a3.subject.outgoing) == 0

    # one guard, not changed
    assert flow.subject.name == "tname"
    assert flow.subject.guard == "tguard"


def test_glue(create):
    """Test flow item gluing to action items."""

    flow = create(ControlFlowItem)
    a1 = create(ActionItem, UML.Action)
    a2 = create(ActionItem, UML.Action)

    glued = allow(flow, flow.head, a1)
    assert glued

    connect(flow, flow.head, a1)

    glued = allow(flow, flow.tail, a2)
    assert glued


def test_connect_to_action_item(create):
    flow = create(ControlFlowItem)
    a1 = create(ActionItem, UML.Action)
    a2 = create(ActionItem, UML.Action)

    connect(flow, flow.head, a1)
    connect(flow, flow.tail, a2)

    assert isinstance(flow.subject, UML.ControlFlow)

    assert len(a1.subject.incoming) == 0
    assert len(a2.subject.incoming) == 1
    assert len(a1.subject.outgoing) == 1
    assert len(a2.subject.outgoing) == 0

    assert flow.subject in a1.subject.outgoing
    assert flow.subject.source is a1.subject
    assert flow.subject in a2.subject.incoming
    assert flow.subject.target is a2.subject


def test_disconnect_from_action_item(create):
    """Test flow item disconnection from action items."""
    flow = create(ControlFlowItem)
    a1 = create(ActionItem, UML.Action)
    a2 = create(ActionItem, UML.Action)

    connect(flow, flow.head, a1)
    connect(flow, flow.tail, a2)

    disconnect(flow, flow.head)
    assert flow.subject is None
    assert len(a1.subject.incoming) == 0
    assert len(a2.subject.incoming) == 0
    assert len(a1.subject.outgoing) == 0
    assert len(a2.subject.outgoing) == 0


def test_reconnect(create, element_factory):
    """Test flow item reconnection."""
    flow = create(ControlFlowItem)
    a1 = create(ActionItem, UML.Action)
    a2 = create(ActionItem, UML.Action)
    a3 = create(ActionItem, UML.Action)

    # a1 -> a2
    connect(flow, flow.head, a1)
    connect(flow, flow.tail, a2)
    f = flow.subject
    f.name = "tname"
    f.guard = "tguard"

    # reconnect: a1 -> a3
    connect(flow, flow.tail, a3)

    assert len(a1.subject.incoming) == 0
    assert len(a1.subject.outgoing) == 1
    # no connections to a2
    assert len(a2.subject.incoming) == 0
    assert len(a2.subject.outgoing) == 0
    # connections to a3 instead
    assert len(a3.subject.incoming) == 1
    assert len(a3.subject.outgoing) == 0

    assert len(element_factory.lselect(UML.ControlFlow)) == 1
    # one guard
    assert flow.subject.name == "tname"
    assert flow.subject.guard == "tguard"


def test_object_flow_reconnection(create):
    """Test object flow becoming control flow due to reconnection."""
    flow = create(ObjectFlowItem)
    a1 = create(ActionItem, UML.Action)
    o1 = create(ObjectNodeItem, UML.ObjectNode)
    o2 = create(ObjectNodeItem, UML.ObjectNode)

    # connect with control flow: a1 -> o1
    connect(flow, flow.head, a1)
    connect(flow, flow.tail, o1)

    f = flow.subject
    f.name = "tname"
    f.guard = "tguard"

    # reconnect with object flow: a1 -> a2
    connect(flow, flow.tail, o2)

    assert len(a1.subject.incoming) == 0
    assert len(a1.subject.outgoing) == 1
    # no connections to o1
    assert len(o1.subject.incoming) == 0
    assert len(o1.subject.outgoing) == 0
    # connections to a2 instead
    assert len(o2.subject.incoming) == 1
    assert len(o2.subject.outgoing) == 0

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

    def test_glue(self, create):
        """Test decision/fork nodes glue."""
        flow = create(ControlFlowItem)
        action = create(ActionItem, UML.Action)
        node = create(self.item_cls, self.join_node_cls)

        glued = allow(flow, flow.head, node)
        assert glued

        connect(flow, flow.head, action)

        glued = allow(flow, flow.tail, node)
        assert glued

    def test_node_class_change(self, create):
        """Test node incoming edges.

        Connection scheme is presented below::

                  head  tail
            [ a1 ]--flow1-->    |
                             [ jn ] --flow3--> [ a3 ]
            [ a2 ]--flow2-->    |

        Node class changes due to two incoming edges and one outgoing edge.
        """
        flow1 = create(ControlFlowItem)
        flow2 = create(ControlFlowItem)
        flow3 = create(ControlFlowItem)
        a1 = create(ActionItem, UML.Action)
        a2 = create(ActionItem, UML.Action)
        jn = create(self.item_cls, self.fork_node_cls)

        assert isinstance(jn.subject, self.fork_node_cls)

        # connect actions first
        connect(flow1, flow1.head, a1)
        connect(flow2, flow2.head, a2)
        connect(flow3, flow3.tail, a2)

        # connect to the node
        connect(flow1, flow1.tail, jn)
        connect(flow2, flow2.tail, jn)
        connect(flow3, flow3.head, jn)

        # node class changes
        assert isinstance(jn.subject, self.join_node_cls)

    def test_outgoing_edges(self, create):
        """Test outgoing edges.

        Connection scheme is presented below::

                   head  tail    | --flow2-->[ a2 ]
            [ a1 ] --flow1--> [ jn ]
                                 | --flow3-->[ a3 ]
        """
        flow1 = create(ControlFlowItem)
        flow2 = create(ControlFlowItem)
        flow3 = create(ControlFlowItem)
        a1 = create(ActionItem, UML.Action)
        a2 = create(ActionItem, UML.Action)
        jn = create(self.item_cls, self.join_node_cls)

        # connect actions first
        connect(flow1, flow1.head, a1)
        connect(flow2, flow2.tail, a2)
        connect(flow3, flow3.tail, a2)

        # connect to the node
        connect(flow1, flow1.tail, jn)
        assert isinstance(jn.subject, self.join_node_cls)

        connect(flow2, flow2.head, jn)
        assert isinstance(jn.subject, self.join_node_cls)

        assert len(jn.subject.incoming) == 1
        assert len(jn.subject.outgoing) == 1
        assert flow1.subject in jn.subject.incoming
        assert flow2.subject in jn.subject.outgoing

        connect(flow3, flow3.head, jn)
        assert len(jn.subject.outgoing) == 2

        assert isinstance(jn.subject, self.fork_node_cls), f"{jn.subject}"

    def test_combined_nodes_connection(self, create):
        """Test combined nodes connection.

        Connection scheme is presented below::

                   head  tail    |   --flow2--> [ a2 ]
            [ a1 ] --flow1--> [ jn ]
            [ a4 ] --flow4-->    |   --flow3--> [ a3 ]

        Flow `flow4` will force the node to become a combined node.
        """
        flow1 = create(ControlFlowItem)
        flow2 = create(ControlFlowItem)
        flow3 = create(ControlFlowItem)
        flow4 = create(ControlFlowItem)
        a1 = create(ActionItem, UML.Action)
        a2 = create(ActionItem, UML.Action)
        a4 = create(ActionItem, UML.Action)
        jn = create(self.item_cls, self.join_node_cls)

        # connect actions first
        connect(flow1, flow1.head, a1)
        connect(flow2, flow2.tail, a2)
        connect(flow3, flow3.tail, a2)
        connect(flow4, flow4.head, a4)

        # connect to the node
        connect(flow1, flow1.tail, jn)
        connect(flow2, flow2.head, jn)
        connect(flow3, flow3.head, jn)

        connect(flow4, flow4.tail, jn)
        assert isinstance(jn.subject, self.join_node_cls)
        assert jn.combined is not None

        # check node combination
        assert len(jn.subject.outgoing) == 1
        assert len(jn.combined.incoming) == 1
        assert jn.subject.outgoing[0] is jn.combined.incoming[0]

    def test_combined_node_disconnection(self, create, element_factory):
        """Test combined nodes disconnection.

        Connection scheme is presented below::

                   head  tail    |   --flow2--> [ a2 ]
            [ a1 ] --flow1--> [ jn ]
            [ a4 ] --flow4-->    |   --flow3--> [ a3 ]

        Flow `flow4` will force the node to become a combined node.
        """
        flow1 = create(ControlFlowItem)
        flow2 = create(ControlFlowItem)
        flow3 = create(ControlFlowItem)
        flow4 = create(ControlFlowItem)
        a1 = create(ActionItem, UML.Action)
        a2 = create(ActionItem, UML.Action)
        a4 = create(ActionItem, UML.Action)
        jn = create(self.item_cls, self.join_node_cls)

        # connect actions first
        connect(flow1, flow1.head, a1)
        connect(flow2, flow2.tail, a2)
        connect(flow3, flow3.tail, a2)
        connect(flow4, flow4.head, a4)

        # connect to the node
        connect(flow1, flow1.tail, jn)
        connect(flow2, flow2.head, jn)
        connect(flow3, flow3.head, jn)
        connect(flow4, flow4.tail, jn)

        # needed for tests below
        cflow = jn.subject.outgoing[0]
        cnode = jn.combined
        assert cflow in element_factory.lselect(UML.ControlFlow)
        assert cnode in element_factory.lselect(self.fork_node_cls)

        # test disconnection
        disconnect(flow4, flow4.head)
        assert get_connected(flow4, flow4.head) is None
        assert jn.combined is None

        flows = element_factory.lselect(UML.ControlFlow)
        nodes = element_factory.lselect(self.fork_node_cls)
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
