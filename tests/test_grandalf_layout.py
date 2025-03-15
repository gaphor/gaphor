from gaphas.segment import Segment
from grandalf.graphs import Edge, Graph, Vertex
from grandalf.layouts import SugiyamaLayout
from grandalf.routing import EdgeViewer

from gaphor.diagram.export import save_png
from gaphor.diagram.general import Box, Line


def test_graph_layout(diagram):
    v1, v2, v3 = Vertex("a"), Vertex("b"), Vertex("c")
    e1, e2, e3 = Edge(v1, v2), Edge(v2, v3), Edge(v1, v3)

    class defaultview:
        w, h = 100, 50  # use object sizes here?

    for v in (v1, v2, v3):
        v.view = defaultview()

    for e in (e1, e2, e3):
        e.view = EdgeViewer()

    g = Graph([v1, v2, v3], [e1, e2, e3])

    layout = SugiyamaLayout(g.C[0])
    layout.xspace = 100
    layout.yspace = 100

    # layout = DigcoLayout(g.C[0])
    # layout.dr = 200

    layout.init_all()
    layout.draw()

    for v in (v1, v2, v3):
        box = diagram.create(Box)
        x, y = v.view.xy
        box.matrix.translate(x - box.width / 2, y - box.height / 2)

    for e in (e1, e2, e3):
        line = diagram.create(Line)

        points = e.view._pts  # noqa: SLF001

        segment = Segment(line, diagram)
        while len(points) > len(line.handles()):
            segment.split_segment(0)
        while len(points) < len(line.handles()):
            segment.merge_segment(0)

        matrix = line.matrix_i2c.inverse()
        for handle, point in zip(line.handles(), points, strict=False):
            handle.pos = matrix.transform_point(*point)

    diagram.update()

    save_png("grandalf.png", diagram)
