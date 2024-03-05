from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.actions.actionspropertypages import (
    DecisionNodePropertyPage,
    FlowPropertyPageAbstract,
    ForkNodePropertyPage,
    JoinNodePropertyPage,
    ObjectNodePropertyPage,
    ShowObjectNodePropertyPage,
)


def test_object_node_property_page_show_ordering(diagram, element_factory):
    item = diagram.create(
        UML.actions.ObjectNodeItem, subject=element_factory.create(UML.ObjectNode)
    )
    property_page = ShowObjectNodePropertyPage(item)

    widget = property_page.construct()
    show_ordering = find(widget, "show-ordering")
    show_ordering.set_active(True)

    assert item.show_ordering


def test_object_node_property_page_upper_bound(diagram, element_factory):
    subject = element_factory.create(UML.ObjectNode)
    property_page = ObjectNodePropertyPage(subject)

    widget = property_page.construct()
    upper_bound = find(widget, "upper-bound")
    upper_bound.set_text("test")

    assert subject.upperBound == "test"


def test_object_node_property_page_ordering(diagram, element_factory):
    subject = element_factory.create(UML.ObjectNode)

    assert subject.ordering == "unordered"
    property_page = ObjectNodePropertyPage(subject)

    widget = property_page.construct()
    ordering = find(widget, "ordering")
    ordering.set_selected(3)

    assert subject.ordering == "FIFO"


def test_decision_node_property_page_show_type(diagram, element_factory):
    item = diagram.create(
        UML.actions.DecisionNodeItem, subject=element_factory.create(UML.DecisionNode)
    )
    property_page = DecisionNodePropertyPage(item)

    widget = property_page.construct()
    show_type = find(widget, "show-type")
    show_type.set_active(True)

    assert item.show_underlying_type


def test_fork_node_property_page(diagram, element_factory):
    item = diagram.create(
        UML.actions.ForkNodeItem, subject=element_factory.create(UML.ForkNode)
    )
    orig_matrix = item.matrix.tuple()
    property_page = ForkNodePropertyPage(item)

    widget = property_page.construct()
    horizontal = find(widget, "horizontal")
    horizontal.set_active(True)

    assert item.matrix.tuple() != orig_matrix


def test_join_node_property_page(element_factory):
    subject = element_factory.create(UML.JoinNode)
    property_page = JoinNodePropertyPage(subject)

    widget = property_page.construct()
    join_spec = find(widget, "join-spec")
    join_spec.set_text("test")

    assert subject.joinSpec == "test"


def test_flow_property_page(element_factory):
    subject = element_factory.create(UML.ObjectFlow)
    property_page = FlowPropertyPageAbstract(subject)

    widget = property_page.construct()
    guard = find(widget, "guard")
    guard.set_text("test")

    assert subject.guard == "test"
