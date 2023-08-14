import io
import base64

from gi.repository import Gtk

from gaphor.core import transactional, gettext
from gaphor.core.modeling import Comment
from gaphor.diagram.general.metadata import MetadataItem
from gaphor.diagram.general.image import ImageItem

from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    handler_blocking,
    new_builder,
    unsubscribe_all_on_destroy,
)

from gaphor.ui.errorhandler import error_handler

from gaphor.diagram.iconname import to_kebab_case
from gaphor.ui.filedialog import open_file_dialog
from PIL import Image as PILImage


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

FILTER_IMAGES = [
    ("Images", "*.png, *.jpg, *.jpeg", "image/*"),
]

@PropertyPages.register(ImageItem)
class ImagePropertyPage(PropertyPageBase):
    """Edit image settings"""

    def __init__(self, subject):
        self.subject = subject
        self.watcher = subject and subject.watcher()

    def construct(self):
        subject = self.subject

        if not subject:
            return

        builder = new_builder("image-editor",
                              signals={
                                "select-image": (self._on_open_image_clicked,),  
                                "set-default-size": (self._on_default_size_clicked),              
                              })
        return builder.get_object("image-editor")
    
    @transactional
    def _on_open_image_clicked(self, button):

        open_file_dialog(
            gettext("Select an image…"),
            self.open_files,
            filters = FILTER_IMAGES
        )
    
    @transactional
    def open_files(self, filenames):
        for filename in filenames:
            with open(filename, 'rb') as file:
                try:
                    image_data = file.read()
                    image = PILImage.open(io.BytesIO(image_data))
                    image.verify()
                    image.close()

                    base64_encoded_data = base64.b64encode(image_data)
                    self.subject.subject.content = base64_encoded_data.decode('ascii')
                    self.subject.subject.dimension = f"{self.subject.width} {self.subject.height}" 
                    return
                except Exception as e:
                    error_handler(
                        message=gettext("Unable to parse image “{filename}”.").format(
                            filename=filename
                        )
                    )            

    @transactional
    def _on_default_size_clicked(self, button):
        if (self.subject and self.subject.subject and self.subject.subject.content):
            base64_img_bytes = self.subject.subject.content.encode('ascii')
            image_data = base64.decodebytes(base64_img_bytes)
            image = PILImage.open(io.BytesIO(image_data))
            
            self.subject.width = image.width
            self.subject.height= image.height

            self.subject.subject.dimension =  f"{image.width} {image.height}"