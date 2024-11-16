import base64
import io
from pathlib import Path

from PIL import Image

from gaphor.core import gettext
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages, new_builder
from gaphor.transaction import Transaction
from gaphor.ui.errorhandler import error_handler
from gaphor.ui.filedialog import open_file_dialog
from gaphor.UML.general.image import ImageItem


@PropertyPages.register(ImageItem)
class ImagePropertyPage(PropertyPageBase):
    """Edit image settings"""

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
            self.open_file,
            image_filter=True,
            parent=button.get_root(),
            multiple=False,
        )

    def open_file(self, filename):
        try:
            with Transaction(self.event_manager):
                self.subject.load_image_from_file(filename)
                if self.subject.subject.name in [
                    None,
                    gettext("New Image"),
                ] and (new_image_name := self.sanitize_image_name(filename)):
                    self.subject.subject.name = new_image_name
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

    def sanitize_image_name(self, filename):
        return "".join(
            chr if chr.isalnum() or (chr in [" ", "_", "-"]) else "_"
            for chr in Path(filename).stem
        )
