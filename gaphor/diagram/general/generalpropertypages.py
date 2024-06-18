import base64
import io

from gi.repository import Gtk
from PIL import Image

from gaphor.core import gettext
from gaphor.core.modeling import Comment
from gaphor.diagram.general.metadata import MetadataItem
from gaphor.diagram.general.picture import PictureItem
from gaphor.diagram.iconname import to_kebab_case
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    handler_blocking,
    new_builder,
    unsubscribe_all_on_destroy,
)
from gaphor.transaction import Transaction
from gaphor.ui.errorhandler import error_handler
from gaphor.ui.filedialog import open_file_dialog


@PropertyPages.register(Comment)
class CommentPropertyPage(PropertyPageBase):
    """Property page for Comments."""

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


@PropertyPages.register(MetadataItem)
class MetadataPropertyPage(PropertyPageBase):
    def __init__(self, item, event_manager):
        self.item = item
        self.event_manager = event_manager
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

    def _on_field_change(self, entry, field_name):
        with Transaction(self.event_manager):
            text = entry.get_text()
            setattr(self.item, field_name, text)


@PropertyPages.register(PictureItem)
class PicturePropertyPage(PropertyPageBase):
    """Edit picture settings"""

    def __init__(self, subject, event_manager):
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject and subject.watcher()

    def construct(self):
        subject = self.subject

        if not subject:
            return

        builder = new_builder(
            "picture-editor",
            signals={
                "select-picture": (self._on_select_picture_clicked,),
                "set-default-size": (self._on_default_size_clicked),
            },
        )
        return builder.get_object("picture-editor")

    def _on_select_picture_clicked(self, button):
        open_file_dialog(
            gettext("Select a picture..."),
            self.open_files,
            image_filter=True,
            parent=button.get_root(),
        )

    def open_files(self, filenames):
        for filename in filenames:
            with open(filename, "rb") as file:
                try:
                    image_data = file.read()
                    image = Image.open(io.BytesIO(image_data))
                    image.verify()
                    image.close()

                    base64_encoded_data = base64.b64encode(image_data)

                    with Transaction(self.event_manager):
                        self.subject.subject.content = base64_encoded_data.decode(
                            "ascii"
                        )
                        self.subject.width = image.width
                        self.subject.height = image.height
                except Exception:
                    error_handler(
                        message=gettext("Unable to parse picture “{filename}”.").format(
                            filename=filename
                        )
                    )

    def _on_default_size_clicked(self, button):
        if self.subject and self.subject.subject and self.subject.subject.content:
            base64_img_bytes = self.subject.subject.content.encode("ascii")
            image_data = base64.decodebytes(base64_img_bytes)
            image = Image.open(io.BytesIO(image_data))

            with Transaction(self.event_manager):
                self.subject.width = image.width
                self.subject.height = image.height
