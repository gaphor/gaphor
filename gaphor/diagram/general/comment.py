"""
CommentItem diagram item
"""


from gaphor.core.modeling import Comment
from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.shapes import Box, Text, stroke
from gaphor.diagram.support import represents
from gaphor.diagram.text import TextAlign, VerticalAlign


@represents(Comment)
class CommentItem(ElementPresentation):
    EAR = 15

    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        OFFSET = 5
        ear = self.EAR
        self.min_width = ear + 2 * OFFSET
        self.height = 50
        self.width = 100

        self.body = Text(
            text=lambda: self.subject.body or "",
            width=lambda: self.width - ear - 2 * OFFSET,
            style={"text-align": TextAlign.LEFT, "vertical-align": VerticalAlign.TOP},
        )

        self.shape = Box(
            self.body,
            style={"padding": (OFFSET, ear + OFFSET, OFFSET, OFFSET)},
            draw=self.draw_border,
        )
        self.watch("subject[Comment].body")

    def draw_border(self, box, context, bounding_box):
        cr = context.cairo
        ear = self.EAR
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
        stroke(context)
