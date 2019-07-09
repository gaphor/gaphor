"""
CommentItem diagram item
"""

from gaphas.item import NW

from gaphor import UML
from gaphor.UML.presentation import ElementPresentation

# from gaphor.diagram.textelement import text_multiline, text_extents
from gaphor.diagram.shapes import Box
from gaphor.diagram.text import TextBox, TextAlign, VerticalAlign, text_size
from gaphor.diagram.support import represents


@represents(UML.Comment)
class CommentItem(ElementPresentation):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        EAR = 15
        OFFSET = 5
        self.min_width = EAR + 2 * OFFSET
        self.height = 50
        self.width = 100

        self.body = TextBox(
            text=lambda: self.subject and self.subject.body or "",
            width=lambda: self.width - EAR - 2 * OFFSET,
            style={"text-align": TextAlign.LEFT, "vertical-align": VerticalAlign.TOP},
        )

        self.layout = Box(
            self.body,
            style={"ear": EAR, "padding": (OFFSET, EAR + OFFSET, OFFSET, OFFSET)},
            draw=self.draw_border,
        )
        self.watch("subject<Comment>.body")

    def draw_border(self, box, context, bounding_box):
        cr = context.cairo
        ear = box.style("ear")
        x, y, w, h = bounding_box
        line_to = cr.line_to
        cr.move_to(w - ear, y)
        line_to(w - ear, y + ear)
        line_to(w, y + ear)
        line_to(w - ear, y)
        line_to(x, y)
        line_to(x, h)
        line_to(w, h)
        line_to(w, y + ear)
        cr.stroke()
