import pytest

from gaphor import UML, SysML
from gaphor.diagram.propertypages import PropertyPages
from gaphor.diagram.tests.fixtures import find
from gaphor.SysML.propertypages import (
    CompartmentPage,
    ItemFlowPropertyPage,
    PropertyPropertyPage,
    RequirementPropertyPage,
)


@pytest.fixture
def connector(element_factory):
    subject = element_factory.create(UML.Connector)
    head_end = element_factory.create(UML.ConnectorEnd)
    head_end.role = element_factory.create(UML.Property)
    tail_end = element_factory.create(UML.ConnectorEnd)
    tail_end.role = element_factory.create(UML.Property)
    subject.end = head_end
    subject.end = tail_end
    return subject


def test_requirement_property_page_id(element_factory):
    subject = element_factory.create(SysML.sysml.Requirement)
    property_page = RequirementPropertyPage(subject)

    widget = property_page.construct()
    requirement_id = find(widget, "requirement-id")
    requirement_id.set_text("test")

    assert subject.externalId == "test"


def test_requirement_property_page_text(diagram, element_factory):
    subject = element_factory.create(SysML.sysml.Requirement)
    property_page = RequirementPropertyPage(subject)

    widget = property_page.construct()
    requirement_text = find(widget, "requirement-text")
    requirement_text.get_buffer().set_text("test")

    assert subject.text == "test"


def test_compartment_property_page_show_parts(diagram, element_factory):
    item = diagram.create(
        SysML.blocks.BlockItem, subject=element_factory.create(SysML.sysml.Block)
    )
    property_page = CompartmentPage(item)

    widget = property_page.construct()
    show_parts = find(widget, "show-parts")
    show_parts.set_active(True)

    assert item.show_parts


def test_compartment_property_page_show_references(diagram, element_factory):
    item = diagram.create(
        SysML.blocks.BlockItem, subject=element_factory.create(SysML.sysml.Block)
    )
    property_page = CompartmentPage(item)

    widget = property_page.construct()
    show_references = find(widget, "show-references")
    show_references.set_active(True)

    assert item.show_references


def test_compartment_property_page_show_values(diagram, element_factory):
    item = diagram.create(
        SysML.blocks.BlockItem, subject=element_factory.create(SysML.sysml.Block)
    )
    property_page = CompartmentPage(item)

    widget = property_page.construct()
    show_references = find(widget, "show-values")
    show_references.set_active(True)

    assert item.show_values


def test_property_property_page(element_factory):
    subject = element_factory.create(SysML.sysml.Property)
    property_page = PropertyPropertyPage(subject)

    widget = property_page.construct()
    show_references = find(widget, "aggregation")
    show_references.set_active(2)

    assert subject.aggregation == "composite"


def test_item_flow(connector):
    property_page = ItemFlowPropertyPage(connector)

    widget = property_page.construct()
    use = find(widget, "use-item-flow")
    use.set_active(True)
    assert connector.informationFlow
    assert connector.informationFlow[0].itemProperty


def test_disable_item_flow(element_factory):
    subject = element_factory.create(SysML.sysml.Connector)
    property_page = ItemFlowPropertyPage(subject)

    widget = property_page.construct()
    use = find(widget, "use-item-flow")
    use.set_active(True)
    use.set_active(False)

    assert not subject.informationFlow


def test_item_flow_name(connector):
    property_page = ItemFlowPropertyPage(connector)

    widget = property_page.construct()
    use = find(widget, "use-item-flow")
    use.set_active(True)
    entry = find(widget, "item-flow-name")
    entry.set_text("foo")

    assert entry.get_text() == "foo"
    assert connector.informationFlow[0].itemProperty.name == "foo"


def test_item_flow_type(connector, element_factory):
    type = element_factory.create(UML.Class)
    type.name = "Bar"
    property_page = ItemFlowPropertyPage(connector)

    widget = property_page.construct()
    use = find(widget, "use-item-flow")
    use.set_active(True)
    combo = find(widget, "item-flow-type")
    combo.set_active_id(type.id)

    assert combo.get_child().get_text() == "Bar"
    assert connector.informationFlow[0].itemProperty.type is type


def test_item_flow_is_loaded(element_factory):
    subject = element_factory.create(UML.Connector)
    property_pages = PropertyPages(subject)

    assert any(isinstance(page, ItemFlowPropertyPage) for page in property_pages)


def test_item_flow_source_and_target(element_factory):
    subject = element_factory.create(UML.Connector)
    head_end = element_factory.create(UML.ConnectorEnd)
    head_end.role = element_factory.create(UML.Property)
    tail_end = element_factory.create(UML.ConnectorEnd)
    tail_end.role = element_factory.create(UML.Property)
    subject.end = head_end
    subject.end = tail_end

    property_page = ItemFlowPropertyPage(subject)

    widget = property_page.construct()
    use = find(widget, "use-item-flow")
    use.set_active(True)

    assert subject.informationFlow[0].informationSource is head_end.role
    assert subject.informationFlow[0].informationTarget is tail_end.role


def test_item_flow_invert_direction(element_factory):
    subject = element_factory.create(UML.Connector)
    head_end = element_factory.create(UML.ConnectorEnd)
    head_end.role = element_factory.create(UML.Property)
    tail_end = element_factory.create(UML.ConnectorEnd)
    tail_end.role = element_factory.create(UML.Property)
    subject.end = head_end
    subject.end = tail_end

    property_page = ItemFlowPropertyPage(subject)

    widget = property_page.construct()
    use = find(widget, "use-item-flow")
    use.set_active(True)

    property_page._invert_direction_changed(None)

    assert subject.informationFlow[0].informationSource is tail_end.role
    assert subject.informationFlow[0].informationTarget is head_end.role
