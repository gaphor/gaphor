from gi.repository import Gdk
from gaphor import UML
from gaphor.UML.actions.activity import ActivityItem
from gaphor.UML.actions.activitypropertypage import (
    ActivityItemPage,
    activity_parameter_node_model,
    list_view_handler,
)
from gaphor.diagram.tests.fixtures import find


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


def test_update_model_when_new_parameter_added(create, element_factory):
    activity_item = create(ActivityItem, UML.Activity)

    property_page = ActivityItemPage(activity_item)
    property_page.construct()

    activity_item.subject.node = activity_parameter_node(element_factory, "one")

    assert property_page.model.get_n_items() == 2  # one + empty row


def test_update_model_when_new_parameter_added_via_list_model(create, element_factory):
    activity_item = create(ActivityItem, UML.Activity)

    property_page = ActivityItemPage(activity_item)
    property_page.construct()

    new_view = property_page.model.get_item(0)
    new_view.parameter = "new"

    assert property_page.model.get_n_items() == 2  # one + empty row
    assert property_page.model.get_item(0).node is new_view.node
    assert property_page.model.get_item(1).node is None


def test_update_model_with_single_node_when_parameter_deleted(create, element_factory):
    activity_item = create(ActivityItem, UML.Activity)
    activity_item.subject.node = node = activity_parameter_node(element_factory, "one")

    property_page = ActivityItemPage(activity_item)
    property_page.construct()

    del activity_item.subject.node[node]

    assert not activity_item.subject.node
    assert property_page.model.get_n_items() == 1
    assert property_page.model.get_item(0).node is None


def test_update_model_with_multiple_nodes_when_parameter_deleted(
    create, element_factory
):
    activity_item = create(ActivityItem, UML.Activity)
    activity_item.subject.node = node = activity_parameter_node(element_factory, "one")
    activity_item.subject.node = activity_parameter_node(element_factory, "two")

    property_page = ActivityItemPage(activity_item)
    property_page.construct()

    del activity_item.subject.node[node]

    assert property_page.model.get_n_items() == 2
    assert property_page.model.get_item(0).node in activity_item.subject.node
    assert property_page.model.get_item(1).node is None


def test_activity_parameter_node_reorder_down(create, element_factory):
    activity_item = create(ActivityItem, UML.Activity)
    activity_item.subject.node = activity_parameter_node(element_factory, "one")
    activity_item.subject.node = activity_parameter_node(element_factory, "two")
    node_one, node_two = activity_item.subject.node

    property_page = ActivityItemPage(activity_item)
    widget = property_page.construct()

    list_view = find(widget, "parameter-list")
    selection = list_view.get_model()

    list_view_handler(None, Gdk.KEY_plus, None, 0, selection)

    assert activity_item.subject.node[0] is node_two
    assert activity_item.subject.node[1] is node_one


def test_activity_parameter_node_reorder_up(create, element_factory):
    activity_item = create(ActivityItem, UML.Activity)
    activity_item.subject.node = activity_parameter_node(element_factory, "one")
    activity_item.subject.node = activity_parameter_node(element_factory, "two")
    node_one, node_two = activity_item.subject.node

    property_page = ActivityItemPage(activity_item)
    widget = property_page.construct()

    list_view = find(widget, "parameter-list")
    selection = list_view.get_model()
    selection.set_selected(1)

    list_view_handler(None, Gdk.KEY_minus, None, 0, selection)

    assert activity_item.subject.node[0] is node_two
    assert activity_item.subject.node[1] is node_one


def test_activity_parameter_node_reorder_first_node_up(create, element_factory):
    activity_item = create(ActivityItem, UML.Activity)
    activity_item.subject.node = activity_parameter_node(element_factory, "one")
    activity_item.subject.node = activity_parameter_node(element_factory, "two")
    node_one, node_two = activity_item.subject.node

    property_page = ActivityItemPage(activity_item)
    widget = property_page.construct()

    list_view = find(widget, "parameter-list")
    selection = list_view.get_model()

    list_view_handler(None, Gdk.KEY_minus, None, 0, selection)

    assert activity_item.subject.node[0] is node_one
    assert activity_item.subject.node[1] is node_two


def test_construct_activity_itemproperty_page(create):
    activity_item = create(ActivityItem, UML.Activity)

    property_page = ActivityItemPage(activity_item)
    widget = property_page.construct()

    assert widget
