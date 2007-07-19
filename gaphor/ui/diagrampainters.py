"""
Painters for diagrams (canvas').

"""

from gaphas.painter import Painter, PainterChain
from gaphas.painter import ItemPainter, HandlePainter, ToolPainter
from gaphas.item import Line
from cairo import Matrix, ANTIALIAS_NONE


class LineSegmentPainter(Painter):
    """
    This painter draws pseudo-hanldes on gaphas.item.Line objects. Each
    line can be split by dragging those points, which will result in
    a new handle.

    ConnectHandleTool take care of performing the user
    interaction required for this feature.
    """

    def paint(self, context):
        view = context.view
        item = view.hovered_item
        if item and item is view.focused_item and isinstance(item, Line):
            cr = context.cairo
            h = item.handles()
            for h1, h2 in zip(h[:-1], h[1:]):
                cx = (h1.x + h2.x) / 2
                cy = (h1.y + h2.y) / 2
                cr.save()
                cr.identity_matrix()
                m = Matrix(*view.get_matrix_i2v(item))

                cr.set_antialias(ANTIALIAS_NONE)
                cr.translate(*m.transform_point(cx, cy))
                cr.rectangle(-3, -3, 6, 6)
                cr.set_source_rgba(0, 0.5, 0, .4)
                cr.fill_preserve()
                cr.set_source_rgba(.25, .25, .25, .6)
                cr.set_line_width(1)
                cr.stroke()
                cr.restore()


def DefaultPainter():
    """
    Default painter, containing item, handle and tool painters.
    """
    chain = PainterChain()
    chain.append(ItemPainter())
    chain.append(HandlePainter())
    chain.append(LineSegmentPainter())
    chain.append(ToolPainter())
    return chain


# vim: sw=4:et:ai
