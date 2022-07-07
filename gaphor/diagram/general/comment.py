"""CommentItem diagram item."""

from functools import partial

from gaphor.core.modeling import Comment
from gaphor.core.styling import TextAlign, VerticalAlign
from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.shapes import Box, Text, stroke
from gaphor.diagram.support import represents


@represents(Comment)
class CommentItem(ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)
        offset = 5
        ear = 15
        self.min_width = ear + 2 * offset
        self.height = 50
        self.width = 100

        self._body = Text(
            text=lambda: self.subject.body or "",
            width=lambda: self.width - ear - 2 * offset,
            style={"text-align": TextAlign.LEFT, "vertical-align": VerticalAlign.TOP},
        )

        self.shape = Box(
            self._body,
            style={"padding": (offset, ear + offset, offset, offset)},
            draw=partial(draw_border, ear=ear),
        )
        self.watch("subject[Comment].body")


def draw_border(box, context, bounding_box, ear):
    cr = context.cairo
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
