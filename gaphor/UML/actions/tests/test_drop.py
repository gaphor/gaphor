from gaphor.diagram.drop import drop
from gaphor.UML import Action, ControlFlow, ObjectFlow, ObjectNode, uml
from gaphor.UML.actions.action import ActionItem
from gaphor.UML.actions.actionstoolbox import partition_config
from gaphor.UML.actions.activity import ActivityItem, ActivityParameterNodeItem
from gaphor.UML.actions.drop import drop_on_partition
from gaphor.UML.actions.partition import PartitionItem


def test_activity_parameter_drop_with_single_activity_and_parameter(
    diagram, element_factory
):
    activity = element_factory.create(uml.Activity)
    activity_item = diagram.create(ActivityItem, subject=activity)

    activity_parameter_node = element_factory.create(uml.ActivityParameterNode)
    activity.node = activity_parameter_node

    parameter_item = drop(activity_parameter_node, diagram, 0, 0)
    assert isinstance(parameter_item, ActivityParameterNodeItem)
    assert parameter_item.subject is activity_parameter_node
    assert parameter_item.parent is activity_item


def test_activity_parameter_drop_with_multiple_activities_and_parameters(
    diagram, element_factory
):
    activity_1 = element_factory.create(uml.Activity)
    activity_2 = element_factory.create(uml.Activity)
    activity_item_1 = diagram.create(ActivityItem, subject=activity_1)
    activity_item_2 = diagram.create(ActivityItem, subject=activity_2)

    activity_parameter_node_1 = element_factory.create(uml.ActivityParameterNode)
    activity_parameter_node_2 = element_factory.create(uml.ActivityParameterNode)
    activity_1.node = activity_parameter_node_1
    activity_2.node = activity_parameter_node_2

    parameter_item_1 = drop(activity_parameter_node_1, diagram, 0, 0)
    parameter_item_2 = drop(activity_parameter_node_2, diagram, 20, 30)

    assert isinstance(parameter_item_1, ActivityParameterNodeItem)
    assert isinstance(parameter_item_2, ActivityParameterNodeItem)
    assert parameter_item_1.subject is activity_parameter_node_1
    assert parameter_item_2.subject is activity_parameter_node_2
    assert parameter_item_1.parent is activity_item_1
    assert parameter_item_2.parent is activity_item_2


def test_activity_parameter_drop_with_two_same_activity_items(diagram, element_factory):
    activity = element_factory.create(uml.Activity)
    activity_item_1 = diagram.create(ActivityItem, subject=activity)
    activity_item_2 = diagram.create(ActivityItem, subject=activity)
    activity_item_1.matrix.translate(50, 50)
    activity_item_2.matrix.translate(300, -200)

    activity_parameter_node = element_factory.create(uml.ActivityParameterNode)
    activity.node = activity_parameter_node

    parameter_item_1 = drop(activity_parameter_node, diagram, 0, 0)
    parameter_item_2 = drop(activity_parameter_node, diagram, 320, -230)

    assert isinstance(parameter_item_1, ActivityParameterNodeItem)
    assert parameter_item_1.subject is activity_parameter_node
    assert parameter_item_1.parent is activity_item_1

    assert isinstance(parameter_item_2, ActivityParameterNodeItem)
    assert parameter_item_2.subject is activity_parameter_node
    assert parameter_item_2.parent is activity_item_2


def test_drop_control_flow(diagram, element_factory):
    a = element_factory.create(Action)
    b = element_factory.create(Action)
    control_flow = element_factory.create(ControlFlow)
    control_flow.source = a
    control_flow.target = b

    drop(a, diagram, 0, 0)
    drop(b, diagram, 0, 0)
    item = drop(control_flow, diagram, 0, 0)

    assert item
    assert diagram.connections.get_connection(item.head).connected is a.presentation[0]
    assert diagram.connections.get_connection(item.tail).connected is b.presentation[0]


def test_drop_object_flow(diagram, element_factory):
    a = element_factory.create(Action)
    b = element_factory.create(ObjectNode)
    control_flow = element_factory.create(ObjectFlow)
    control_flow.source = a
    control_flow.target = b

    drop(a, diagram, 0, 0)
    drop(b, diagram, 0, 0)
    item = drop(control_flow, diagram, 0, 0)

    assert item
    assert diagram.connections.get_connection(item.head).connected is a.presentation[0]
    assert diagram.connections.get_connection(item.tail).connected is b.presentation[0]


def test_drop_on_swimlane_on_first_partition(create):
    swimlanes: PartitionItem = create(PartitionItem, uml.ActivityPartition)
    partition_config(swimlanes)
    action = create(ActionItem, uml.Action)

    drop_on_partition(action, swimlanes, 10, swimlanes.height / 2)

    assert action.subject in swimlanes.partition[0].node


def test_drop_on_swimlane_on_second_partition(create):
    swimlanes: PartitionItem = create(PartitionItem, uml.ActivityPartition)
    partition_config(swimlanes)
    action = create(ActionItem, uml.Action)

    drop_on_partition(action, swimlanes, swimlanes.width - 10, swimlanes.height / 2)

    assert action.subject in swimlanes.partition[1].node


def test_drop_from_first_swimlane_on_second_partition(create):
    swimlanes: PartitionItem = create(PartitionItem, uml.ActivityPartition)
    partition_config(swimlanes)
    action = create(ActionItem, uml.Action)

    handles = swimlanes.handles()
    drop_on_partition(action, swimlanes, handles[0].pos.x + 10, swimlanes.height / 2)
    drop_on_partition(action, swimlanes, handles[1].pos.x - 10, swimlanes.height / 2)

    assert action.subject not in swimlanes.partition[0].node
    assert action.subject in swimlanes.partition[1].node


def test_drop_from_second_swimlane_to_outside(create):
    swimlanes: PartitionItem = create(PartitionItem, uml.ActivityPartition)
    partition_config(swimlanes)
    action = create(ActionItem, uml.Action)

    handles = swimlanes.handles()
    drop_on_partition(action, swimlanes, handles[1].pos.x - 10, swimlanes.height / 2)
    drop_on_partition(action, swimlanes, handles[1].pos.x - 10, 1000)

    assert action.subject not in swimlanes.partition[0].node
    assert action.subject not in swimlanes.partition[1].node
