from gi.repository import Gtk

from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    handler_blocking,
    new_builder,
    unsubscribe_all_on_destroy,
)
from gaphor.transaction import Transaction
from gaphor.UML import Comment


@PropertyPages.register(Comment)
class CommentPropertyPage(PropertyPageBase):
    """Property page for Comments."""

    order = 10

    def __init__(self, subject, event_manager):
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject and subject.watcher()

    def construct(self):
        subject = self.subject

        if not subject:
            return

        builder = new_builder("comment-editor")
        text_view = builder.get_object("comment")

        buffer = Gtk.TextBuffer()
        if subject.body:
            buffer.set_text(subject.body)
        text_view.set_buffer(buffer)

        @handler_blocking(buffer, "changed", self._on_body_change)
        def handler(event):
            if not text_view.props.has_focus:
                buffer.set_text(event.new_value or "")

        self.watcher.watch("body", handler)

        return unsubscribe_all_on_destroy(
            builder.get_object("comment-editor"), self.watcher
        )

    def _on_body_change(self, buffer):
        with Transaction(self.event_manager):
            self.subject.body = buffer.get_text(
                buffer.get_start_iter(), buffer.get_end_iter(), False
            )
