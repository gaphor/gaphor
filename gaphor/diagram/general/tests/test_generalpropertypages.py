import pytest

from gaphor.core.modeling import Diagram
from gaphor.diagram.general import Box, Diamond, Ellipse, Line, MetadataItem
from gaphor.diagram.general.generalpropertypages import (
    LabelPropertyPage,
    LineEndPropertyPage,
    MetadataPropertyPage,
)
from gaphor.diagram.general.simpleitem import LineEndStyle
from gaphor.diagram.tests.fixtures import find


@pytest.mark.parametrize("item_type", [Box, Diamond, Ellipse, Line])
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


def test_line_end_property_page_head_and_tail(element_factory, event_manager):
    diagram = element_factory.create(Diagram)
    line = diagram.create(Line)

    property_page = LineEndPropertyPage(line, event_manager)
    widget = property_page.construct()

    head = find(widget, "line-head-end")
    tail = find(widget, "line-tail-end")

    head.set_selected(2)
    tail.set_selected(3)

    assert line.head_end == LineEndStyle.triangle
    assert line.tail_end == LineEndStyle.diamond


def test_line_end_property_page_allows_independent_values(
    element_factory, event_manager
):
    diagram = element_factory.create(Diagram)
    line = diagram.create(Line)

    property_page = LineEndPropertyPage(line, event_manager)
    widget = property_page.construct()

    head = find(widget, "line-head-end")
    tail = find(widget, "line-tail-end")

    head.set_selected(1)
    tail.set_selected(0)

    assert line.head_end == LineEndStyle.arrow
    assert line.tail_end == LineEndStyle.none
