from gi.repository import Gdk

from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.actions.activitypropertypage import (
    ActivityPage,
    ActivityParameterNodeDirectionPropertyPage,
    ActivityParameterNodeNamePropertyPage,
    ActivityParameterNodeTypePropertyPage,
    activity_parameter_node_model,
    list_view_key_handler,
)


def activity_parameter_node(element_factory, name=None):
    node = element_factory.create(UML.ActivityParameterNode)
    node.parameter = element_factory.create(UML.Parameter)
    node.name = name
    return node


def test_activity_parameter_node_empty(element_factory, event_manager):
    activity = element_factory.create(UML.Activity)
    model = activity_parameter_node_model(activity, event_manager)

    empty = model.get_item(0)

    assert not empty.node


def test_activity_parameter_node_in_model(element_factory, event_manager):
    activity = element_factory.create(UML.Activity)
    activity.node = activity_parameter_node(element_factory, "name")
    model = activity_parameter_node_model(activity, event_manager)

    param = model.get_item(0)
    empty = model.get_item(1)

    assert param.node is activity.node[0]
    assert not empty.node


def test_activity_parameter_node_edit_existing_parameter(
    element_factory, event_manager
):
    activity = element_factory.create(UML.Activity)
    activity.node = activity_parameter_node(element_factory)
    parameter = activity.node[0].parameter
    model = activity_parameter_node_model(activity, event_manager)

    view = model.get_item(0)
    view.parameter = "in attr: str"

    assert parameter.direction == "in"
    assert parameter.name == "attr"
    assert parameter.typeValue == "str"


def test_activity_parameter_node_add_new_parameter(element_factory, event_manager):
    activity = element_factory.create(UML.Activity)
    model = activity_parameter_node_model(activity, event_manager)

    view = model.get_item(0)
    view.parameter = "in attr: str"
    parameter = activity.node[0].parameter

    assert view.node in activity.node
    assert parameter.direction == "in"
    assert parameter.name == "attr"
    assert parameter.typeValue == "str"


def test_update_model_when_new_parameter_added(element_factory, event_manager):
    subject = element_factory.create(UML.Activity)

    property_page = ActivityPage(subject, event_manager)
    property_page.construct()

    subject.node = activity_parameter_node(element_factory, "one")

    assert property_page.model.get_n_items() == 2  # one + empty row


def test_activity_parameter_node_name_editing(element_factory, event_manager):
    subject = element_factory.create(UML.ActivityParameterNode)
    subject.parameter = element_factory.create(UML.Parameter)
    property_page = ActivityParameterNodeNamePropertyPage(subject, event_manager)

    widget = property_page.construct()
    name = find(widget, "name-entry")
    name.set_text("A new name")

    assert subject.parameter.name == "A new name"


def test_update_model_when_new_parameter_added_via_list_model(
    element_factory, event_manager
):
    subject = element_factory.create(UML.Activity)

    property_page = ActivityPage(subject, event_manager)
    property_page.construct()

    new_view = property_page.model.get_item(0)
    new_view.parameter = "new"

    assert property_page.model.get_n_items() == 2  # one + empty row
    assert property_page.model.get_item(0).node is new_view.node
    assert property_page.model.get_item(1).node is None


def test_update_model_with_single_node_when_parameter_deleted(
    element_factory, event_manager
):
    subject = element_factory.create(UML.Activity)
    subject.node = node = activity_parameter_node(element_factory, "one")

    property_page = ActivityPage(subject, event_manager)
    property_page.construct()

    del subject.node[node]

    assert not subject.node
    assert property_page.model.get_n_items() == 1
    assert property_page.model.get_item(0).node is None


def test_update_model_with_multiple_nodes_when_parameter_deleted(
    element_factory, event_manager
):
    subject = element_factory.create(UML.Activity)
    subject.node = node = activity_parameter_node(element_factory, "one")
    subject.node = activity_parameter_node(element_factory, "two")

    property_page = ActivityPage(subject, event_manager)
    property_page.construct()

    del subject.node[node]

    assert property_page.model.get_n_items() == 2
    assert property_page.model.get_item(0).node in subject.node
    assert property_page.model.get_item(1).node is None


def test_activity_parameter_node_reorder_down(element_factory, event_manager):
    subject = element_factory.create(UML.Activity)
    subject.node = activity_parameter_node(element_factory, "one")
    subject.node = activity_parameter_node(element_factory, "two")
    node_one, node_two = subject.node

    property_page = ActivityPage(subject, event_manager)
    widget = property_page.construct()

    list_view = find(widget, "parameter-list")

    list_view_key_handler(ControllerStub(list_view), Gdk.KEY_plus, None, 0)

    assert subject.node[0] is node_two
    assert subject.node[1] is node_one


def test_activity_parameter_node_reorder_up(element_factory, event_manager):
    subject = element_factory.create(UML.Activity)
    subject.node = activity_parameter_node(element_factory, "one")
    subject.node = activity_parameter_node(element_factory, "two")
    node_one, node_two = subject.node

    property_page = ActivityPage(subject, event_manager)
    widget = property_page.construct()

    list_view = find(widget, "parameter-list")
    selection = list_view.get_model()
    selection.set_selected(1)

    list_view_key_handler(ControllerStub(list_view), Gdk.KEY_minus, None, 0)

    assert subject.node[0] is node_two
    assert subject.node[1] is node_one


def test_activity_parameter_node_reorder_first_node_up(element_factory, event_manager):
    subject = element_factory.create(UML.Activity)
    subject.node = activity_parameter_node(element_factory, "one")
    subject.node = activity_parameter_node(element_factory, "two")
    node_one, node_two = subject.node

    property_page = ActivityPage(subject, event_manager)
    widget = property_page.construct()

    list_view = find(widget, "parameter-list")

    list_view_key_handler(ControllerStub(list_view), Gdk.KEY_minus, None, 0)

    assert subject.node[0] is node_one
    assert subject.node[1] is node_two


def test_construct_activity_item_property_page(element_factory, event_manager):
    subject = element_factory.create(UML.Activity)

    property_page = ActivityPage(subject, event_manager)
    widget = property_page.construct()

    assert widget


def test_construct_activity_parameter_node_type_property_page(
    element_factory, event_manager
):
    subject = element_factory.create(UML.ActivityParameterNode)
    subject.parameter = element_factory.create(UML.Parameter)

    property_page = ActivityParameterNodeTypePropertyPage(subject, event_manager)
    widget = property_page.construct()

    assert widget


def test_construct_activity_parameter_node_direction_property_page(
    element_factory, event_manager
):
    subject = element_factory.create(UML.ActivityParameterNode)
    subject.parameter = element_factory.create(UML.Parameter)

    property_page = ActivityParameterNodeDirectionPropertyPage(subject, event_manager)
    widget = property_page.construct()

    assert widget


def test_construct_activity_parameter_node_direction_changed(
    element_factory, event_manager
):
    subject = element_factory.create(UML.ActivityParameterNode)
    subject.parameter = element_factory.create(UML.Parameter)

    property_page = ActivityParameterNodeDirectionPropertyPage(subject, event_manager)
    widget = property_page.construct()

    direction = find(widget, "parameter-direction")
    direction.set_selected(3)

    assert subject.parameter.direction == "return"


class ControllerStub:
    def __init__(self, widget):
        self._widget = widget

    def get_widget(self):
        return self._widget
