import pytest

from gaphor import UML, SysML
from gaphor.diagram.presentation import DEFAULT_HEIGHT
from gaphor.diagram.propertypages import PropertyPages
from gaphor.diagram.tests.fixtures import find
from gaphor.SysML.propertypages import (
    CompartmentPage,
    ItemFlowPropertyPage,
    PropertyAggregationPropertyPage,
    RequirementItemPropertyPage,
    RequirementPropertyPage,
)
from gaphor.UML.propertypages import (
    ShowTypedElementPropertyPage,
    TypedElementPropertyPage,
)


@pytest.fixture
def association(element_factory):
    class_a = element_factory.create(UML.Class)
    class_b = element_factory.create(UML.Class)
    return UML.recipes.create_association(class_a, class_b)


@pytest.fixture
def connector(element_factory):
    prop_a = element_factory.create(UML.Property)
    prop_b = element_factory.create(UML.Property)
    return UML.recipes.create_connector(prop_a, prop_b)


def test_requirement_property_page_id(element_factory, event_manager):
    subject = element_factory.create(SysML.sysml.Requirement)
    property_page = RequirementPropertyPage(subject, event_manager)

    widget = property_page.construct()
    requirement_id = find(widget, "requirement-id")
    requirement_id.set_text("test")

    assert subject.externalId == "test"


def test_requirement_property_page_text(element_factory, event_manager):
    subject = element_factory.create(SysML.sysml.Requirement)
    property_page = RequirementPropertyPage(subject, event_manager)

    widget = property_page.construct()
    requirement_text = find(widget, "requirement-text")
    requirement_text.get_buffer().set_text("test")

    assert subject.text == "test"


def test_requirement_property_page_show_text(diagram, element_factory, event_manager):
    item = diagram.create(
        SysML.requirements.RequirementItem,
        subject=element_factory.create(SysML.sysml.Requirement),
    )
    property_page = RequirementItemPropertyPage(item, event_manager)

    widget = property_page.construct()
    show_requirement_text = find(widget, "show-requirement-text")

    assert item.show_text
    show_requirement_text.set_active(False)
    assert ~item.show_text


def test_requirement_height_reset(diagram, element_factory):
    item = diagram.create(
        SysML.requirements.RequirementItem,
        subject=element_factory.create(SysML.sysml.Requirement),
    )
    item.height = 500
    assert item.height == 500

    item.subject.text = "test"
    assert item.height == DEFAULT_HEIGHT


def test_show_property_type_property_page_show_type(
    diagram, element_factory, event_manager
):
    item = diagram.create(
        SysML.blocks.ProxyPortItem,
        subject=element_factory.create(SysML.sysml.ProxyPort),
    )
    property_page = ShowTypedElementPropertyPage(item, event_manager)

    widget = property_page.construct()
    show_parts = find(widget, "show-type")
    show_parts.set_active(True)

    assert item.show_type


def test_compartment_property_page_show_parts(diagram, element_factory, event_manager):
    item = diagram.create(
        SysML.blocks.BlockItem, subject=element_factory.create(SysML.sysml.Block)
    )
    property_page = CompartmentPage(item, event_manager)

    widget = property_page.construct()
    show_parts = find(widget, "show-parts")
    show_parts.set_active(True)

    assert item.show_parts


def test_compartment_property_page_show_references(
    diagram, element_factory, event_manager
):
    item = diagram.create(
        SysML.blocks.BlockItem, subject=element_factory.create(SysML.sysml.Block)
    )
    property_page = CompartmentPage(item, event_manager)

    widget = property_page.construct()
    show_references = find(widget, "show-references")
    show_references.set_active(True)

    assert item.show_references


def test_compartment_property_page_show_values(diagram, element_factory, event_manager):
    item = diagram.create(
        SysML.blocks.BlockItem, subject=element_factory.create(SysML.sysml.Block)
    )
    property_page = CompartmentPage(item, event_manager)

    widget = property_page.construct()
    show_references = find(widget, "show-values")
    show_references.set_active(True)

    assert item.show_values


def test_property_aggregation_page(element_factory, event_manager):
    subject = element_factory.create(SysML.sysml.Property)
    property_page = PropertyAggregationPropertyPage(subject, event_manager)

    widget = property_page.construct()
    show_references = find(widget, "aggregation")
    show_references.set_selected(2)

    assert subject.aggregation == "composite"


def test_no_property_aggregation_page_for_ports(element_factory, event_manager):
    subject = element_factory.create(UML.Port)
    property_page = PropertyAggregationPropertyPage(subject, event_manager)

    widget = property_page.construct()

    assert not widget


def test_property_type(element_factory, event_manager):
    subject = element_factory.create(UML.Property)

    type = element_factory.create(UML.Class)
    type.name = "Bar"
    property_page = TypedElementPropertyPage(subject, event_manager)

    widget = property_page.construct()
    dropdown = find(widget, "element-type")
    bar_index = next(
        n for n, lv in enumerate(dropdown.get_model()) if lv.value == type.id
    )
    dropdown.set_selected(bar_index)

    assert dropdown.get_selected_item().label == "Bar"
    assert subject.type is type


def test_association_item_flow(association, event_manager):
    property_page = ItemFlowPropertyPage(association, event_manager)

    widget = property_page.construct()
    use = find(widget, "use-item-flow")
    use.set_active(True)

    assert association.abstraction
    assert association.abstraction[0].itemProperty
    assert association.abstraction[0].informationSource is association.memberEnd[0]
    assert association.abstraction[0].informationTarget is association.memberEnd[1]


def test_connector_item_flow(connector, event_manager):
    property_page = ItemFlowPropertyPage(connector, event_manager)

    widget = property_page.construct()
    use = find(widget, "use-item-flow")
    use.set_active(True)

    assert connector.informationFlow
    assert connector.informationFlow[0].itemProperty


def test_disable_item_flow(element_factory, event_manager):
    subject = element_factory.create(SysML.sysml.Connector)
    property_page = ItemFlowPropertyPage(subject, event_manager)

    widget = property_page.construct()
    use = find(widget, "use-item-flow")
    use.set_active(True)
    use.set_active(False)

    assert not subject.informationFlow


def test_item_flow_name(connector, event_manager):
    property_page = ItemFlowPropertyPage(connector, event_manager)

    widget = property_page.construct()
    use = find(widget, "use-item-flow")
    use.set_active(True)
    entry = find(widget, "item-flow-name")
    entry.set_text("foo")

    assert entry.get_text() == "foo"
    assert connector.informationFlow[0].itemProperty.name == "foo"


def test_item_flow_type(connector, element_factory, event_manager):
    type = element_factory.create(UML.Class)
    type.name = "Bar"
    property_page = ItemFlowPropertyPage(connector, event_manager)

    widget = property_page.construct()
    use = find(widget, "use-item-flow")
    use.set_active(True)
    dropdown = find(widget, "item-flow-type")
    bar_index = next(
        n for n, lv in enumerate(dropdown.get_model()) if lv.value == type.id
    )
    dropdown.set_selected(bar_index)

    assert dropdown.get_selected_item().label == "Bar"
    assert connector.informationFlow[0].itemProperty.type is type


def test_item_flow_is_loaded(element_factory):
    subject = element_factory.create(UML.Connector)
    property_pages = PropertyPages.find(subject)

    assert any(issubclass(page, ItemFlowPropertyPage) for page in property_pages)


def test_item_flow_source_and_target(element_factory, event_manager):
    subject = element_factory.create(UML.Connector)
    head_end = element_factory.create(UML.ConnectorEnd)
    head_end.role = element_factory.create(UML.Property)
    tail_end = element_factory.create(UML.ConnectorEnd)
    tail_end.role = element_factory.create(UML.Property)
    subject.end = head_end
    subject.end = tail_end

    property_page = ItemFlowPropertyPage(subject, event_manager)

    widget = property_page.construct()
    use = find(widget, "use-item-flow")
    use.set_active(True)

    assert subject.informationFlow[0].informationSource is head_end.role
    assert subject.informationFlow[0].informationTarget is tail_end.role


def test_connector_item_flow_invert_direction(connector, event_manager):
    property_page = ItemFlowPropertyPage(connector, event_manager)

    widget = property_page.construct()
    use = find(widget, "use-item-flow")
    use.set_active(True)

    property_page.on_invert_direction_changed(None)

    information_flow = connector.informationFlow[0]
    assert information_flow.informationSource is connector.end[1].role
    assert information_flow.informationTarget is connector.end[0].role


def test_association_item_flow_invert_direction(association, event_manager):
    property_page = ItemFlowPropertyPage(association, event_manager)

    widget = property_page.construct()
    use = find(widget, "use-item-flow")
    use.set_active(True)

    property_page.on_invert_direction_changed(None)

    information_flow = association.abstraction[0]
    assert information_flow.informationSource is association.memberEnd[1]
    assert information_flow.informationTarget is association.memberEnd[0]
