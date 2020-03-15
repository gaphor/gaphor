from gi.repository import Gtk

from gaphor import UML
from gaphor.core import gettext, transactional
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages, new_builder


@PropertyPages.register(UML.Comment)
class CommentItemPropertyPage(PropertyPageBase):
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

        changed_id = buffer.connect("changed", self._on_body_change)

        def handler(event):
            if not text_view.props.has_focus:
                buffer.handler_block(changed_id)
                buffer.set_text(event.new_value)
                buffer.handler_unblock(changed_id)

        self.watcher.watch("body", handler).subscribe_all()
        text_view.connect("destroy", self.watcher.unsubscribe_all)

        return builder.get_object("comment-editor")

    @transactional
    def _on_body_change(self, buffer):
        self.subject.body = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), False
        )
