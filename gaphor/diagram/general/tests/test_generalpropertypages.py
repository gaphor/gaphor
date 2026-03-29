import pytest

from gaphor.core.modeling import Diagram
from gaphor.diagram.general import Box, Ellipse, Line, MetadataItem
from gaphor.diagram.general.generalpropertypages import (
    LabelPropertyPage,
    MetadataPropertyPage,
)
from gaphor.diagram.tests.fixtures import find


@pytest.mark.parametrize("item_type", [Box, Ellipse, Line])
def test_name_page(element_factory, event_manager, item_type):
    diagram = element_factory.create(Diagram)
    item = diagram.create(item_type)
    property_page = LabelPropertyPage(item, event_manager)
    widget = property_page.construct()
    name = find(widget, "label-entry")
    name.set_text("A new label")

    assert item.label == "A new label"


def test_name_page_disposal(element_factory, event_manager):
    diagram = element_factory.create(Diagram)
    item = diagram.create(Box)
    property_page = LabelPropertyPage(item, event_manager)
    binding_ref = property_page.binding.weak_ref()
    widget_ref = property_page.construct().weak_ref()
    property_page.close()
    del property_page

    assert widget_ref() is None
    assert binding_ref() is None


def test_metadata_property_page(diagram, event_manager):
    metadata = diagram.create(MetadataItem)

    property_page = MetadataPropertyPage(metadata, event_manager)

    widget = property_page.construct()
    description = find(widget, "description")
    description.set_text("my text")

    assert metadata.description == "my text"
