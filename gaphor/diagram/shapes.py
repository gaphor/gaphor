from math import atan2
from gaphor.diagram.text import Text, text_point_at_line


class Box:
    def __init__(self, *children, style={}, draw=None):
        self.children = children
        self.style = {
            "min-width": 0,
            "min-height": 0,
            "padding": (0, 0, 0, 0),
            **style,
        }.__getitem__
        self._draw = draw

    def size(self, cr):
        style = self.style
        min_width = style("min-width")
        min_height = style("min-height")
        padding = style("padding")
        sizes = [c.size(cr) for c in self.children]
        if sizes:
            widths, heights = list(zip(*sizes))
            return (
                max(min_width, max(widths) + padding[1] + padding[3]),
                max(min_height, sum(heights) + padding[0] + padding[2]),
            )
        else:
            return 0, 0

    def draw(self, cr, bounding_box):
        if self._draw:
            self._draw(self, cr, bounding_box)
        for c in self.children:
            c.draw(cr, bounding_box)


def draw_default_head(line, cr):
    """
    Default head drawer: move cursor to the first handle.
    """
    cr.move_to(0, 0)


def draw_default_tail(line, cr):
    """
    Default tail drawer: draw line to the last handle.
    """
    cr.line_to(0, 0)


def draw_arrow_tail(line, cr):
    cr.line_to(0, 0)
    cr.stroke()
    cr.move_to(15, -6)
    cr.line_to(0, 0)
    cr.line_to(15, 6)


class Line:
    def __init__(
        self,
        *children,
        style={},
        draw_head=draw_default_head,
        draw_tail=draw_default_tail,
    ):
        super().__init__()
        self.children = children
        self.style = {"dash-style": (), "line-width": 2, **style}.__getitem__
        self._draw_head = draw_head
        self._draw_tail = draw_tail

    def size(self, cr, points):
        return 0, 0

    def draw(self, cr, points):
        def draw_line_end(p0, p1, draw):
            x0, y0 = p0
            x1, y1 = p1
            angle = atan2(y1 - y0, x1 - x0)
            cr.save()
            try:
                cr.translate(*p0)
                cr.rotate(angle)
                draw(self, cr)
            finally:
                cr.restore()

        cr.set_line_width(self.style("line-width"))
        draw_line_end(points[0], points[1], self._draw_head)
        if self.style("dash-style"):
            cr.set_dash(self.style("dash-style"), 0)
        for p in points[1:-1]:
            cr.line_to(*p)
        draw_line_end(points[-1], points[-2], self._draw_tail)
        cr.stroke()

        for c in self.children:
            assert isinstance(c, Text), f"All children should be of type Text ({c})"
            size = c.size(cr)
            x, y = text_point_at_line(
                points,
                size,
                c.style("text-align"),
                c.style("vertical-align"),
                c.style("padding"),
            )
            c.draw(cr, (x, y))
