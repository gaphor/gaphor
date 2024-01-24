"""CommentItem diagram item."""


from gaphor.core.modeling import Comment
from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.shapes import Box, CssNode, Text, stroke
from gaphor.diagram.support import represents


@represents(Comment)
class CommentItem(ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)
        self.height = 50
        self.width = 100

        self.shape = Box(
            CssNode(
                "body",
                None,
                Text(
                    text=lambda: self.subject.body or "",
                ),
            ),
            draw=draw_border,
        )
        self.watch("subject[Comment].body")


def draw_border(box, context, bounding_box):
    cr = context.cairo
    x, y, w, h = bounding_box
    _, padding_right, _, padding_left = context.style.get("padding", (4, 16, 4, 4))
    ear = max(padding_right - padding_left, padding_left)
    line_to = cr.line_to
    cr.move_to(w - ear, y)
    line_to(w - ear, y + ear)
    line_to(w, y + ear)
    line_to(w - ear, y)
    line_to(x, y)
    line_to(x, h)
    line_to(w, h)
    line_to(w, y + ear)
    stroke(context, fill=True)
