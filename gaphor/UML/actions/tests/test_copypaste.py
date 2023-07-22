from gaphor.diagram.copypaste import copy_full, paste_full, paste_link
from gaphor.UML import Activity, ActivityParameterNode, Parameter
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
