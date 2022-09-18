from functools import singledispatch

import pydot
from gaphas.connector import ConnectionSink, Connector
from gaphas.segment import Segment

from gaphor.abc import ActionProvider, Service
from gaphor.action import action
from gaphor.core.modeling import Diagram, Presentation
from gaphor.diagram.presentation import ElementPresentation, LinePresentation
from gaphor.i18n import gettext
from gaphor.transaction import Transaction
from gaphor.UML.classes.generalization import GeneralizationItem

DPI = 72.0


class AutoLayout(Service, ActionProvider):
    def __init__(self, event_manager, diagrams, tools_menu=None, dump_gv=True):
        self.event_manager = event_manager
        self.diagrams = diagrams
        if tools_menu:
            tools_menu.add_actions(self)
        self.dump_gv = dump_gv

    def shutdown(self):
        pass

    @action(
        name="auto-layout", label=gettext("Auto Layout"), shortcut="<Primary><Shift>L"
    )
    def layout_current_diagram(self):
        if current_diagram := self.diagrams.get_current_diagram():
            self.layout(current_diagram)

    def layout(self, diagram: Diagram):
        rendered_graph = self.render(diagram)
        self.apply_layout(diagram, rendered_graph)

    def render(self, diagram: Diagram):
        graph = pydot.Dot(
            "gaphor", graph_type="graph", prog="neato", splines="polyline"
        )

        for presentation in diagram.ownedPresentation:
            edge_or_node = as_pydot(presentation)

            if isinstance(edge_or_node, pydot.Edge):
                graph.add_edge(edge_or_node)
            elif isinstance(edge_or_node, pydot.Node):
                graph.add_node(edge_or_node)

        rendered_string = graph.create(format="dot").decode("utf-8")
        if self.dump_gv:
            with open("auto_layout.gv", "w") as f:
                f.write(rendered_string)

        rendered_graphs = pydot.graph_from_dot_data(rendered_string)
        return rendered_graphs[0]

    def apply_layout(self, diagram, rendered_graph):
        _, _, _, height = parse_bb(rendered_graph.get_node("graph")[0].get("bb"))
        offset = 10

        with Transaction(self.event_manager):
            for node in rendered_graph.get_nodes():
                name = node.get_name().replace('"', "")
                if presentation := next(
                    (p for p in diagram.ownedPresentation if p.id == name), None
                ):
                    pos = parse_point(node.get_pos())
                    presentation.matrix.set(
                        x0=pos[0] - presentation.width / 2 + offset,
                        y0=height - pos[1] - presentation.height / 2 + offset,
                    )
                    presentation.request_update()

            for edge in rendered_graph.get_edges():
                id = strip_quotes(edge.get("id"))
                if presentation := next(
                    (p for p in diagram.ownedPresentation if p.id == id), None
                ):
                    points = parse_edge_pos(edge.get_pos())

                    if isinstance(presentation, GeneralizationItem):
                        points.reverse()

                    presentation.orthogonal = False
                    segment = Segment(presentation, diagram)
                    while len(points) > len(presentation.handles()):
                        segment.split_segment(0)
                    while 2 < len(points) < len(presentation.handles()):
                        segment.merge_segment(0)

                    matrix = presentation.matrix_i2c.inverse()
                    for handle, point in zip(presentation.handles(), points):
                        p = matrix.transform_point(
                            point[0] + offset, height - point[1] + offset
                        )
                        handle.pos = p

                    for handle in (presentation.head, presentation.tail):
                        reconnect(presentation, handle, diagram.connections)


def reconnect(presentation, handle, connections):
    if not (connected := connections.get_connection(handle)):
        return

    connector = Connector(presentation, handle, connections)
    sink = ConnectionSink(connected.connected, distance=float("inf"))
    connector.glue(sink)
    connector.connect(sink)


@singledispatch
def as_pydot(presentation: Presentation):
    return None


@as_pydot.register
def _(presentation: ElementPresentation):
    return pydot.Node(
        presentation.id,
        label="",
        shape="rect",
        width=presentation.width / DPI,
        height=presentation.height / DPI,
    )


@as_pydot.register
def _(presentation: LinePresentation):
    connections = presentation.diagram.connections
    head_element = connections.get_connection(presentation.head)
    tail_element = connections.get_connection(presentation.tail)
    if isinstance(head_element, ElementPresentation) and isinstance(
        tail_element, ElementPresentation
    ):
        return pydot.Edge(
            head_element.connected.id, tail_element.connected.id, id=presentation.id
        )
    return None


@as_pydot.register
def _(presentation: GeneralizationItem):
    # Tail and head are reverse
    connections = presentation.diagram.connections
    head_element = connections.get_connection(presentation.head)
    tail_element = connections.get_connection(presentation.tail)
    if head_element and tail_element:
        return pydot.Edge(
            tail_element.connected.id, head_element.connected.id, id=presentation.id
        )
    return None


def parse_edge_pos(pos_str: str) -> list[tuple[float, float]]:
    raw_points = strip_quotes(pos_str).split(" ")

    points = [parse_point(raw_points.pop(0))]

    while raw_points:
        raw_points.pop(0)
        raw_points.pop(0)
        points.append(parse_point(raw_points.pop(0)))
    return points


def parse_point(point):
    x, y = strip_quotes(point).split(",")
    return (float(x), float(y))


def parse_bb(bb):
    x, y, w, h = strip_quotes(bb).split(",")
    return (float(x), float(y), float(w), float(h))


def strip_quotes(s):
    return s.replace('"', "")
