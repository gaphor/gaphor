from gi.repository import Gtk

from gaphor.core import transactional
from gaphor.core.modeling import Comment
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    handler_blocking,
    new_builder,
)


@PropertyPages.register(Comment)
class CommentPropertyPage(PropertyPageBase):
    """Property page for Comments."""

    def __init__(self, subject):
        self.subject = subject
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
        text_view.connect("destroy", self.watcher.unsubscribe_all)

        return builder.get_object("comment-editor")

    @transactional
    def _on_body_change(self, buffer):
        self.subject.body = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), False
        )
