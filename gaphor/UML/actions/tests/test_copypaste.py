from gaphor.diagram.copypaste import copy_full, paste_full, paste_link
from gaphor.UML import (
    Activity,
    ActivityParameterNode,
    InputPin,
    JoinNode,
    LiteralInteger,
    ObjectNode,
    Parameter,
)
from gaphor.UML.actions.activity import ActivityItem


def test_shallow_copy_activity_with_parameter(diagram, element_factory):
    activity_item = diagram.create(
        ActivityItem, subject=element_factory.create(Activity)
    )
    node = element_factory.create(ActivityParameterNode)
    activity_item.subject.node = node
    node.parameter = element_factory.create(Parameter)

    copy_data = copy_full({activity_item})

    new_elements = paste_link(copy_data, diagram)
    new_activity_item = next(
        (e for e in new_elements if isinstance(e, ActivityItem)), None
    )

    assert new_activity_item, new_elements
    assert new_activity_item.children
    assert new_activity_item.children[0].subject is node


def test_deep_copy_activity_with_parameter(diagram, element_factory):
    activity_item = diagram.create(
        ActivityItem, subject=element_factory.create(Activity)
    )
    node = element_factory.create(ActivityParameterNode)
    activity_item.subject.node = node
    node.parameter = element_factory.create(Parameter)
    node.parameter.name = "Name"

    copy_data = copy_full({activity_item})
    new_elements = paste_full(copy_data, diagram)
    new_activity_item = next(
        (e for e in new_elements if isinstance(e, ActivityItem)), None
    )

    assert new_activity_item, new_elements
    assert new_activity_item.children
    assert new_activity_item.children[0].subject is not node
    assert new_activity_item.children[0].subject.parameter.name == node.parameter.name


def test_do_not_copy_activity_parameter_node(diagram, element_factory):
    activity_item = diagram.create(
        ActivityItem, subject=element_factory.create(Activity)
    )
    node = element_factory.create(ActivityParameterNode)
    activity_item.subject.node = node
    node.parameter = element_factory.create(Parameter)

    copy_data = copy_full(activity_item.children)

    assert activity_item.children
    assert not copy_data.elements


def test_copy_pin(diagram, element_factory):
    pin = element_factory.create(InputPin)
    pin.lowerValue = element_factory.create(LiteralInteger)
    pin.lowerValue.value = 1
    pin.upperValue = element_factory.create(LiteralInteger)
    pin.upperValue.value = 2

    buffer = copy_full({pin})
    paste_full(buffer, diagram)

    new_pin = next(p for p in element_factory.select(InputPin) if p is not pin)

    assert new_pin.lowerValue
    assert new_pin.upperValue
    assert new_pin.lowerValue.value == 1
    assert new_pin.upperValue.value == 2

    assert new_pin.lowerValue is not pin.lowerValue
    assert new_pin.upperValue is not pin.upperValue


def test_copy_object_node(diagram, element_factory):
    node = element_factory.create(ObjectNode)
    node.upperBound = element_factory.create(LiteralInteger)
    node.upperBound.value = 1

    buffer = copy_full({node})
    paste_full(buffer, diagram)

    new_node = next(p for p in element_factory.select(ObjectNode) if p is not node)

    assert new_node.upperBound
    assert new_node.upperBound.value == 1

    assert new_node.upperBound is not node.upperBound


def test_copy_join_node(diagram, element_factory):
    node = element_factory.create(JoinNode)
    node.joinSpec = element_factory.create(LiteralInteger)
    node.joinSpec.value = 1

    buffer = copy_full({node})
    paste_full(buffer, diagram)

    new_node = next(p for p in element_factory.select(JoinNode) if p is not node)

    assert new_node.joinSpec
    assert new_node.joinSpec.value == 1

    assert new_node.joinSpec is not node.joinSpec
