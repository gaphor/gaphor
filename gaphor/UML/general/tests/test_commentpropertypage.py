from gaphor.diagram.tests.fixtures import find
from gaphor.UML import Comment
from gaphor.UML.general.commentpropertypage import CommentPropertyPage


def test_comment_property_page_body(element_factory, event_manager):
    subject = element_factory.create(Comment)
    property_page = CommentPropertyPage(subject, event_manager)

    widget = property_page.construct()
    comment = find(widget, "comment")
    comment.get_buffer().set_text("test")

    assert subject.body == "test"


def test_comment_property_page_update_text(element_factory, event_manager):
    subject = element_factory.create(Comment)
    property_page = CommentPropertyPage(subject, event_manager)

    widget = property_page.construct()
    comment = find(widget, "comment")
    subject.body = "test"
    buffer = comment.get_buffer()

    assert (
        buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False) == "test"
    )
