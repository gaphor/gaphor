from gi.repository import Gtk

from gaphor.core import transactional
from gaphor.core.modeling import Comment
from gaphor.diagram.general.metadata import MetadataItem
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    handler_blocking,
    new_builder,
    unsubscribe_all_on_destroy,
)
from gaphor.diagram.iconname import to_kebab_case


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

        return unsubscribe_all_on_destroy(
            builder.get_object("comment-editor"), self.watcher
        )

    @transactional
    def _on_body_change(self, buffer):
        self.subject.body = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), False
        )


@PropertyPages.register(MetadataItem)
class MetadataPropertyPage(PropertyPageBase):
    def __init__(self, item):
        self.item = item
        self.watcher = item and item.watcher()

    def construct(self):
        attrs = [
            "createdBy",
            "description",
            "website",
            "revision",
            "license",
            "createdOn",
            "updatedOn",
        ]

        builder = new_builder(
            "metadata-editor",
            signals={
                f"{to_kebab_case(a)}-changed": (self._on_field_change, a) for a in attrs
            },
        )

        item = self.item

        for a in attrs:
            builder.get_object(f"{to_kebab_case(a)}").set_text(getattr(item, a) or "")

        return builder.get_object("metadata-editor")

    @transactional
    def _on_field_change(self, entry, field_name):
        text = entry.get_text()
        setattr(self.item, field_name, text)
