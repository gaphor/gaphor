from gi.repository import Gtk

from gaphor import UML
from gaphor.core import _, transactional
from gaphor.diagram.propertypages import PropertyPages, PropertyPageBase


@PropertyPages.register(UML.Comment)
class CommentItemPropertyPage(PropertyPageBase):
    """Property page for Comments."""

    order = 0

    def __init__(self, subject):
        self.subject = subject
        self.watcher = subject and subject.watcher()

    def construct(self):
        subject = self.subject
        page = Gtk.VBox()

        if not subject:
            return page

        label = Gtk.Label(label=_("Comment"))
        label.set_justify(Gtk.Justification.LEFT)
        page.pack_start(label, False, True, 0)

        buffer = Gtk.TextBuffer()
        if subject.body:
            buffer.set_text(subject.body)
        text_view = Gtk.TextView()
        text_view.set_buffer(buffer)
        text_view.show()
        text_view.set_size_request(-1, 100)
        page.pack_start(text_view, True, True, 0)
        page.default = text_view

        changed_id = buffer.connect("changed", self._on_body_change)

        def handler(event):
            if not text_view.props.has_focus:
                buffer.handler_block(changed_id)
                buffer.set_text(event.new_value)
                buffer.handler_unblock(changed_id)

        self.watcher.watch("body", handler).subscribe_all()
        text_view.connect("destroy", self.watcher.unsubscribe_all)

        return page

    @transactional
    def _on_body_change(self, buffer):
        self.subject.body = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), False
        )
