from gi.repository import Gtk

from gaphor import UML
from gaphor.UML.actions.activity import ActivityItem
from gaphor.UML.actions.activitypropertypage import ActivityItemPage, ActivityParameters


def test_activity_parameter_node_editing(create):
    activity_item = create(ActivityItem, UML.Activity)
    model = ActivityParameters(activity_item)
    model.append([None, None])
    path = Gtk.TreePath.new_first()
    iter = model.get_iter(path)
    model.update(iter, col=0, value="param")

    assert model[iter][-1] is activity_item.subject.node[0]


def test_activity_parameter_node_reorder(create, element_factory):
    activity_item = create(ActivityItem, UML.Activity)

    def activity_parameter_node(name):
        node = element_factory.create(UML.ActivityParameterNode)
        node.parameter = element_factory.create(UML.Parameter)
        node.name = name
        activity_item.subject.node = node
        return node

    node1 = activity_parameter_node("param1")
    node2 = activity_parameter_node("param2")
    node3 = activity_parameter_node("param3")

    list_store = ActivityParameters(activity_item)

    new_order = [node3, node1, node2]
    list_store.sync_model(new_order)

    assert activity_item.subject.node[0] is node3
    assert activity_item.subject.node[1] is node1
    assert activity_item.subject.node[2] is node2


def test_activity_page_add_attribute(create):
    activity_item = create(ActivityItem, UML.Activity)
    property_page = ActivityItemPage(activity_item)

    property_page.construct()
    iter = property_page.model.get_iter((0,))
    property_page.model.update(iter, 0, "in attr: str")

    assert activity_item.subject.node[0].parameter.direction == "in"
    assert activity_item.subject.node[0].parameter.name == "attr"
    assert activity_item.subject.node[0].parameter.typeValue == "str"
