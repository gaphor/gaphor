"""Flow item connection adapters tests."""


import pytest as pytest

from gaphor import UML
from gaphor.diagram.tests.fixtures import allow, connect, disconnect, get_connected
from gaphor.UML.actions.action import ActionItem
from gaphor.UML.actions.activity import ActivityItem, ActivityParameterNodeItem
from gaphor.UML.actions.activitynodes import (
    ActivityFinalNodeItem,
    DecisionNodeItem,
    FlowFinalNodeItem,
    ForkNodeItem,
    InitialNodeItem,
)
from gaphor.UML.actions.flow import ControlFlowItem, ObjectFlowItem
from gaphor.UML.actions.objectnode import ObjectNodeItem
from gaphor.UML.actions.pin import InputPinItem, OutputPinItem


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


def test_glue_to_activity_parameter_node(create, element_factory):
    flow = create(ObjectFlowItem)
    anode = create(ActivityParameterNodeItem, UML.ActivityParameterNode)

    glued = allow(flow, flow.head, anode)

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


def test_connect_to_activity_parameter_node(create, element_factory):
    flow = create(ObjectFlowItem)
    activity = create(ActivityItem, UML.Activity)
    param_node = element_factory.create(UML.ActivityParameterNode)
    param_node.parameter = element_factory.create(UML.Parameter)
    activity.subject.node = param_node
    anode = param_node.presentation[0]
    onode = create(ObjectNodeItem, UML.ObjectNode)

    connect(flow, flow.head, anode)
    connect(flow, flow.tail, onode)
    assert flow.subject
    assert isinstance(flow.subject, UML.ObjectFlow)


def test_do_not_allow_head_to_input_pin(create):
    flow = create(ObjectFlowItem)
    pin = create(InputPinItem, UML.InputPin)

    assert not allow(flow, flow.head, pin)
    assert allow(flow, flow.tail, pin)


def test_connect_tail_to_input_pin(create):
    flow = create(ObjectFlowItem)
    pin = create(InputPinItem, UML.InputPin)
    onode = create(ObjectNodeItem, UML.ObjectNode)

    connect(flow, flow.head, onode)
    connect(flow, flow.tail, pin)

    assert flow.subject
    assert isinstance(flow.subject, UML.ObjectFlow)


def test_do_not_allow_tail_to_output_pin(create):
    flow = create(ObjectFlowItem)
    pin = create(OutputPinItem, UML.OutputPin)

    assert allow(flow, flow.head, pin)
    assert not allow(flow, flow.tail, pin)


def test_connect_head_to_output_pin(create):
    flow = create(ObjectFlowItem)
    pin = create(OutputPinItem, UML.OutputPin)
    onode = create(ObjectNodeItem, UML.ObjectNode)

    connect(flow, flow.head, pin)
    connect(flow, flow.tail, onode)

    assert flow.subject
    assert isinstance(flow.subject, UML.ObjectFlow)


def test_object_flow_activity_is_set_on_output_pin(create):
    activity = create(ActivityItem, UML.Activity)
    action = create(ActionItem, UML.Action)
    action.subject.activity = activity.subject

    out_pin = create(OutputPinItem, UML.OutputPin)
    connect(out_pin, out_pin.handles()[0], action)

    in_pin = create(InputPinItem, UML.InputPin)
    flow = create(ObjectFlowItem)
    connect(flow, flow.head, out_pin)
    connect(flow, flow.tail, in_pin)

    assert flow.subject.owner is activity.subject


def test_object_flow_activity_is_set_on_input_pin(create):
    activity = create(ActivityItem, UML.Activity)
    action = create(ActionItem, UML.Action)
    action.subject.activity = activity.subject

    in_pin = create(InputPinItem, UML.InputPin)
    connect(in_pin, in_pin.handles()[0], action)

    out_pin = create(OutputPinItem, UML.OutputPin)
    flow = create(ObjectFlowItem)
    connect(flow, flow.head, out_pin)
    connect(flow, flow.tail, in_pin)

    assert flow.subject.owner is activity.subject


def test_object_flow_reconnect(create, element_factory, sanitizer_service):
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


def test_control_flow_reconnection(create, sanitizer_service):
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


def test_disconnect_from_action_item(create, sanitizer_service):
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


def test_reconnect(create, element_factory, sanitizer_service):
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


def test_object_flow_reconnection(create, sanitizer_service):
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


fork_and_decision_items = pytest.mark.parametrize(
    "item_cls,fork_node_cls,join_node_cls",
    [
        [ForkNodeItem, UML.ForkNode, UML.JoinNode],
        [DecisionNodeItem, UML.DecisionNode, UML.MergeNode],
    ],
)


@fork_and_decision_items
@pytest.mark.parametrize("flow_item", [ControlFlowItem, ObjectFlowItem])
def test_glue_flow_item(create, item_cls, fork_node_cls, join_node_cls, flow_item):
    """Test decision/fork nodes glue."""
    flow = create(flow_item)
    action = create(ActionItem, UML.Action)
    node = create(item_cls, join_node_cls)

    glued = allow(flow, flow.head, node)
    assert glued

    connect(flow, flow.head, action)

    glued = allow(flow, flow.tail, node)
    assert glued


@fork_and_decision_items
@pytest.mark.parametrize("flow_item", [ControlFlowItem, ObjectFlowItem])
def test_node_class_change(create, item_cls, fork_node_cls, join_node_cls, flow_item):
    """Test node incoming edges.

    Connection scheme is presented below::

                head  tail
        [ a1 ]--flow1-->    |
                            [ jn ] --flow3--> [ a3 ]
        [ a2 ]--flow2-->    |

    Node class changes due to two incoming edges and one outgoing edge.
    """
    flow1 = create(flow_item)
    flow2 = create(flow_item)
    flow3 = create(flow_item)
    a1 = create(ActionItem, UML.Action)
    a2 = create(ActionItem, UML.Action)
    jn = create(item_cls, fork_node_cls)

    assert isinstance(jn.subject, fork_node_cls)

    # connect actions first
    connect(flow1, flow1.head, a1)
    connect(flow2, flow2.head, a2)
    connect(flow3, flow3.tail, a2)

    # connect to the node
    connect(flow1, flow1.tail, jn)
    connect(flow2, flow2.tail, jn)
    connect(flow3, flow3.head, jn)

    # node class changes
    assert isinstance(jn.subject, join_node_cls)


@fork_and_decision_items
@pytest.mark.parametrize("flow_item", [ControlFlowItem, ObjectFlowItem])
def test_outgoing_edges(create, item_cls, fork_node_cls, join_node_cls, flow_item):
    """Test outgoing edges.

    Connection scheme is presented below::

                head  tail    | --flow2-->[ a2 ]
        [ a1 ] --flow1--> [ jn ]
                                | --flow3-->[ a3 ]
    """
    flow1 = create(flow_item)
    flow2 = create(flow_item)
    flow3 = create(flow_item)
    a1 = create(ActionItem, UML.Action)
    a2 = create(ActionItem, UML.Action)
    jn = create(item_cls, join_node_cls)

    # connect actions first
    connect(flow1, flow1.head, a1)
    connect(flow2, flow2.tail, a2)
    connect(flow3, flow3.tail, a2)

    # connect to the node
    connect(flow1, flow1.tail, jn)
    assert isinstance(jn.subject, join_node_cls)

    connect(flow2, flow2.head, jn)
    assert isinstance(jn.subject, join_node_cls)

    assert len(jn.subject.incoming) == 1
    assert len(jn.subject.outgoing) == 1
    assert flow1.subject in jn.subject.incoming
    assert flow2.subject in jn.subject.outgoing

    connect(flow3, flow3.head, jn)
    assert len(jn.subject.outgoing) == 2

    assert isinstance(jn.subject, fork_node_cls), f"{jn.subject}"


@fork_and_decision_items
@pytest.mark.parametrize("flow_item", [ControlFlowItem, ObjectFlowItem])
def test_combined_nodes_connection(
    create, item_cls, fork_node_cls, join_node_cls, flow_item
):
    """Test combined nodes connection.

    Connection scheme is presented below::

                head  tail    |   --flow2--> [ a2 ]
        [ a1 ] --flow1--> [ jn ]
        [ a4 ] --flow4-->    |   --flow3--> [ a3 ]

    Flow `flow4` will force the node to become a combined node.
    """
    flow1 = create(flow_item)
    flow2 = create(flow_item)
    flow3 = create(flow_item)
    flow4 = create(flow_item)
    a1 = create(ActionItem, UML.Action)
    a2 = create(ActionItem, UML.Action)
    a4 = create(ActionItem, UML.Action)
    jn = create(item_cls, join_node_cls)

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
    assert isinstance(jn.subject, join_node_cls)
    assert jn.combined is not None

    # check node combination
    assert len(jn.subject.outgoing) == 1
    assert len(jn.combined.incoming) == 1
    assert jn.subject.outgoing[0] is jn.combined.incoming[0]


@fork_and_decision_items
@pytest.mark.parametrize(
    "flow_item,uml_flow",
    [(ControlFlowItem, UML.ControlFlow), (ObjectFlowItem, UML.ObjectFlow)],
)
def test_combined_node_disconnection(
    create,
    element_factory,
    item_cls,
    fork_node_cls,
    join_node_cls,
    flow_item,
    uml_flow,
    sanitizer_service,
):
    """Test combined nodes disconnection.

    Connection scheme is presented below::

                head  tail    |   --flow2--> [ a2 ]
        [ a1 ] --flow1--> [ jn ]
        [ a4 ] --flow4-->    |   --flow3--> [ a3 ]

    Flow `flow4` will force the node to become a combined node.
    """
    flow1 = create(flow_item)
    flow2 = create(flow_item)
    flow3 = create(flow_item)
    flow4 = create(flow_item)
    a1 = create(ActionItem, UML.Action)
    a2 = create(ActionItem, UML.Action)
    a4 = create(ActionItem, UML.Action)
    jn = create(item_cls, join_node_cls)

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
    flow = jn.subject.outgoing[0]
    node = jn.combined

    assert flow in element_factory.lselect(uml_flow)
    assert node in element_factory.lselect(fork_node_cls)

    # test disconnection
    disconnect(flow4, flow4.head)
    assert get_connected(flow4, flow4.head) is None

    assert jn.combined is None

    flows = element_factory.lselect(uml_flow)
    nodes = element_factory.lselect(fork_node_cls)
    assert node not in nodes, f"{node} in {nodes}"
    assert flow not in flows, f"{flow} in {flows}"
