"""PictureItem diagram item."""

import base64
import io

import cairo
from PIL import Image

from gaphor.core.modeling import Picture
from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.shapes import Box, IconBox
from gaphor.diagram.support import represents


@represents(Picture)
class PictureItem(ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.width = 200
        self.height = 200

        self.shape = IconBox(Box(draw=self.draw_image))

        self.watch("subject[Picture].content")

    def create_default_surface(self):
        width = int(self.width)
        height = int(self.height)

        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        ctx = cairo.Context(surface)

        # Draw a white background

        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(1)

        # Draw a border

        ctx.rectangle(0, 0, width - 1, height - 1)
        ctx.stroke()

        # Draw an X

        ctx.move_to(0, 0)
        ctx.line_to(width - 1, height - 1)
        ctx.stroke()

        ctx.move_to(width - 1, 0)
        ctx.line_to(0, height - 1)
        ctx.stroke()

        return 1.0, surface

    def create_content_surface(self):
        base64_img_bytes = self.subject.content.encode("ascii")
        image_data = base64.decodebytes(base64_img_bytes)
        image = Image.open(io.BytesIO(image_data))
        surface = self._from_pil(image)

        surface_width = surface.get_width()
        surface_height = surface.get_height()

        width_ratio = float(self.width) / float(surface_width)
        height_ratio = float(self.height) / float(surface_height)
        scale_xy = min(height_ratio, width_ratio)

        return scale_xy, surface

    def draw_image(self, box, context, bounding_box):
        scale_xy = 1.0
        surface = None

        if not self.subject or not self.subject.content:
            scale_xy, surface = self.create_default_surface()
        else:
            scale_xy, surface = self.create_content_surface()

        cr = context.cairo
        cr.save()
        cr.scale(scale_xy, scale_xy)
        cr.set_source_surface(surface, 0, 0)
        cr.paint()
        cr.restore()

        context_width = surface.get_width() * scale_xy
        context_height = surface.get_height() * scale_xy
        self.width = min(self.width, context_width)
        self.height = min(self.height, context_height)

    def _from_pil(
        self,
        im: Image,
        alpha: float = 1.0,
        format: cairo.Format = cairo.FORMAT_ARGB32,
    ) -> cairo.ImageSurface:
        """Create a new Cairo image surface from a Pillow Image

        Args:
            im (Image): Pillow Image
            alpha (float): 0..1 alpha to add to non-alpha images
            format (cairo.Format): Pixel format for output surface

        Returns:
            cairo.ImageSurface: The image surface representing the pillow image
        """
        assert format in (
            cairo.FORMAT_RGB24,
            cairo.FORMAT_ARGB32,
        ), f"Unsupported pixel format: {format}"
        if "A" not in im.getbands():
            im.putalpha(int(alpha * 256.0))
        arr = bytearray(im.tobytes("raw", "BGRa"))
        return cairo.ImageSurface.create_for_data(arr, format, im.width, im.height)
