"""PictureItem diagram item."""

import base64
import io

import cairo
from gaphas.constraint import BaseConstraint
from gaphas.item import NW, SE
from gaphas.solver import VERY_STRONG, variable
from PIL import Image as PILImage

from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.shapes import Box, IconBox
from gaphor.diagram.support import represents
from gaphor.UML.uml import Image


class AspectRatioConstraint(BaseConstraint):
    def __init__(self, x0, y0, x1, y1, ratio):
        super().__init__(x0, y0, x1, y1, ratio)

    def solve_for(self, var):
        x0, y0, x1, y1, ratio = self.variables()

        if var is x0:
            d = y1.value - y0.value
            x0.value = x1.value - d * ratio
        elif var is x1:
            d = y1.value - y0.value
            x1.value = x0.value + d * ratio
        elif var is y0:
            d = x1.value - x0.value
            y0.value = y1.value - d / ratio
        else:
            d = x1.value - x0.value
            y1.value = y0.value + d / ratio


@represents(Image)
class ImageItem(ElementPresentation[Image]):
    ratio = variable(strength=VERY_STRONG, varname="_ratio")

    def __init__(self, diagram, id=None):
        super().__init__(
            diagram, id, width=10, height=10, shape=IconBox(Box(draw=self.draw_image))
        )

        self.width = 100
        self.height = 100
        self.ratio = 1.0
        self._surface = None

        diagram.connections.add_constraint(
            self,
            AspectRatioConstraint(  # type: ignore[call-arg]
                *self.handles()[NW].pos, *self.handles()[SE].pos, self.ratio
            ),
        )

        self.watch("subject[Image].content", self.update_image)

        self.update_image()

    def postload(self):
        self.update_image()
        return super().postload()

    def update_image(self, event=None):
        if self.subject and self.subject.content:
            self._surface = create_content_surface(self.subject.content.encode("ascii"))
            self.ratio = float(self._surface.get_width()) / float(
                self._surface.get_height()
            )
        else:
            self._surface = None
            self.ratio = 1.0

    def draw_image(self, box, context, bounding_box):
        if self._surface:
            cr = context.cairo
            cr.save()
            cr.scale(
                self.width / self._surface.get_width(),
                self.height / self._surface.get_height(),
            )
            cr.set_source_surface(self._surface, 0, 0)
            cr.paint()
            cr.restore()
        else:
            draw_no_image(context.cairo, self.width, self.height)

    def load_image_from_file(self, filename):
        with open(filename, "rb") as file:
            image_data = file.read()
            with PILImage.open(io.BytesIO(image_data)) as image:
                image.verify()

                self.subject.content = base64.b64encode(image_data).decode("ascii")
                self.width = image.width
                self.height = image.height


def create_content_surface(base64_img_bytes):
    image_data = base64.decodebytes(base64_img_bytes)
    image = PILImage.open(io.BytesIO(image_data))
    return image_surface_from_pil(image)


def draw_no_image(cr, width, height):
    # Draw a white background
    cr.set_source_rgb(1, 1, 1)
    cr.rectangle(0, 0, width, height)
    cr.fill()

    cr.set_source_rgb(0, 0, 0)
    cr.set_line_width(1)

    # Draw a border
    cr.rectangle(0, 0, width - 1, height - 1)
    cr.stroke()

    # Draw an X
    cr.move_to(0, 0)
    cr.line_to(width - 1, height - 1)
    cr.stroke()

    cr.move_to(width - 1, 0)
    cr.line_to(0, height - 1)
    cr.stroke()


def image_surface_from_pil(
    im: PILImage,
    alpha: float = 1.0,
    format: cairo.Format = cairo.FORMAT_ARGB32,
) -> cairo.ImageSurface:
    """Create a new Cairo image surface from a Pillow Image

    Args:
        im: Pillow Image
        alpha: 0..1 alpha to add to non-alpha images
        format: Pixel format for output surface

    Returns:
        The image surface representing the pillow image
    """
    assert format in (
        cairo.FORMAT_RGB24,
        cairo.FORMAT_ARGB32,
    ), f"Unsupported pixel format: {format}"
    if "A" not in im.getbands():
        im.putalpha(int(alpha * 256.0))
    arr = bytearray(im.tobytes("raw", "BGRa"))
    return cairo.ImageSurface.create_for_data(arr, format, im.width, im.height)
