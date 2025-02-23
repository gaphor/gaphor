import asyncio
import base64
import io
from pathlib import Path

from PIL import Image

from gaphor.core import gettext
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages, new_builder
from gaphor.transaction import Transaction
from gaphor.ui.errordialog import error_dialog
from gaphor.ui.filedialog import open_file_dialog
from gaphor.UML.general.image import ImageItem


@PropertyPages.register(ImageItem)
class ImagePropertyPage(PropertyPageBase):
    """Edit image settings"""

    def __init__(self, subject, event_manager):
        super().__init__()
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject and subject.watcher()
        self.background_task = None

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

    async def open_file(self, parent):
        filename: Path = await open_file_dialog(  # type: ignore[assignment]
            gettext("Select a picture..."),
            image_filter=True,
            parent=parent,
            multiple=False,
        )
        if not filename:
            return

        with open(filename, "rb") as file:
            try:
                image_data = file.read()
                image = Image.open(io.BytesIO(image_data))
                image.verify()
                image.close()

                base64_encoded_data = base64.b64encode(image_data)

                with Transaction(self.event_manager):
                    self.subject.subject.content = base64_encoded_data.decode("ascii")
                    self.subject.width = image.width
                    self.subject.height = image.height
                    if self.subject.subject.name in [
                        None,
                        gettext("New Image"),
                    ] and (new_image_name := self.sanitize_image_name(filename)):
                        self.subject.subject.name = new_image_name
            except Exception:
                await error_dialog(
                    message=gettext("Unable to parse picture “{filename}”.").format(
                        filename=filename
                    )
                )

    def _on_select_picture_clicked(self, button):
        if self.background_task and not self.background_task.done():
            return

        self.background_task = asyncio.create_task(self.open_file(button.get_root()))

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
