from gaphor.diagram.general import MetadataItem
from gaphor.diagram.general.generalpropertypages import (
    MetadataPropertyPage,
)
from gaphor.diagram.tests.fixtures import find


def test_metadata_property_page(diagram, event_manager):
    metadata = diagram.create(MetadataItem)

    property_page = MetadataPropertyPage(metadata, event_manager)

    widget = property_page.construct()
    description = find(widget, "description")
    description.set_text("my text")

    assert metadata.description == "my text"
