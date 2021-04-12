from gaphor import SysML
from gaphor.diagram.tests.fixtures import find
from gaphor.SysML.propertypages import (
    PartsAndReferencesPage,
    PropertyPropertyPage,
    RequirementPropertyPage,
)


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


def test_part_and_reference_property_page_show_parts(diagram, element_factory):
    item = diagram.create(
        SysML.blocks.BlockItem, subject=element_factory.create(SysML.sysml.Block)
    )
    property_page = PartsAndReferencesPage(item)

    widget = property_page.construct()
    show_parts = find(widget, "show-parts")
    show_parts.set_active(True)

    assert item.show_parts


def test_part_and_reference_property_page_show_references(diagram, element_factory):
    item = diagram.create(
        SysML.blocks.BlockItem, subject=element_factory.create(SysML.sysml.Block)
    )
    property_page = PartsAndReferencesPage(item)

    widget = property_page.construct()
    show_references = find(widget, "show-references")
    show_references.set_active(True)

    assert item.show_references


def test_property_property_page(element_factory):
    subject = element_factory.create(SysML.sysml.Property)
    property_page = PropertyPropertyPage(subject)

    widget = property_page.construct()
    show_references = find(widget, "aggregation")
    show_references.set_active(2)

    assert subject.aggregation == "composite"
