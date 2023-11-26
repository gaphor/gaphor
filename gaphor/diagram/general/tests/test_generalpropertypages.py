from gaphor.core.modeling import Comment
from gaphor.diagram.general import MetadataItem
from gaphor.diagram.general.generalpropertypages import (
    CommentPropertyPage,
    MetadataPropertyPage,
)
from gaphor.diagram.tests.fixtures import find


def test_comment_property_page_body(element_factory):
    subject = element_factory.create(Comment)
    property_page = CommentPropertyPage(subject)

    widget = property_page.construct()
    comment = find(widget, "comment")
    comment.get_buffer().set_text("test")

    assert subject.body == "test"


def test_comment_property_page_update_text(element_factory):
    subject = element_factory.create(Comment)
    property_page = CommentPropertyPage(subject)

    widget = property_page.construct()
    comment = find(widget, "comment")
    subject.body = "test"
    buffer = comment.get_buffer()

    assert (
        buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False) == "test"
    )


def test_metadata_property_page(diagram):
    metadata = diagram.create(MetadataItem)

    property_page = MetadataPropertyPage(metadata)

    widget = property_page.construct()
    description = find(widget, "description")
    description.set_text("my text")

    assert metadata.description == "my text"
