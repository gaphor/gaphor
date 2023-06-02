import pytest

from gaphor import UML
from gaphor.UML.actions.activitypropertypage import (
    activity_parameter_node_model,
)


def activity_parameter_node(element_factory, name=None):
    node = element_factory.create(UML.ActivityParameterNode)
    node.parameter = element_factory.create(UML.Parameter)
    node.name = name
    return node


def test_activity_parameter_node_empty(element_factory):
    activity = element_factory.create(UML.Activity)
    model = activity_parameter_node_model(activity)

    empty = model.get_item(0)

    assert not empty.node


def test_activity_parameter_node_in_model(element_factory):
    activity = element_factory.create(UML.Activity)
    activity.node = activity_parameter_node(element_factory, "name")
    model = activity_parameter_node_model(activity)

    param = model.get_item(0)
    empty = model.get_item(1)

    assert param.node is activity.node[0]
    assert not empty.node


def test_activity_parameter_node_edit_existing_parameter(element_factory):
    activity = element_factory.create(UML.Activity)
    activity.node = activity_parameter_node(element_factory)
    parameter = activity.node[0].parameter
    model = activity_parameter_node_model(activity)

    view = model.get_item(0)
    view.parameter = "in attr: str"

    assert parameter.direction == "in"
    assert parameter.name == "attr"
    assert parameter.typeValue == "str"


def test_activity_parameter_node_add_new_parameter(element_factory):
    activity = element_factory.create(UML.Activity)
    model = activity_parameter_node_model(activity)

    view = model.get_item(0)
    view.parameter = "in attr: str"
    parameter = activity.node[0].parameter

    assert view.node in activity.node
    assert parameter.direction == "in"
    assert parameter.name == "attr"
    assert parameter.typeValue == "str"


@pytest.mark.skip
def test_activity_parameter_node_reorder(create, element_factory):
    ...
