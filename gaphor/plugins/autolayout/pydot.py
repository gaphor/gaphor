from __future__ import annotations

from functools import singledispatch
from typing import Iterable

import pydot
from gaphas.connector import ConnectionSink, Connector
from gaphas.segment import Segment

from gaphor.abc import ActionProvider, Service
from gaphor.action import action
from gaphor.core.modeling import Diagram, Element
from gaphor.diagram.presentation import (
    AttachedPresentation,
    ElementPresentation,
    LinePresentation,
)
from gaphor.i18n import gettext
from gaphor.transaction import Transaction
from gaphor.UML import NamedElement
from gaphor.UML.actions.activitynodes import ForkNodeItem

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
        graph = diagram_as_pydot(diagram)
        graph.write("before.gv")
        rendered_string = graph.create(format="dot").decode("utf-8")
        if self.dump_gv:
            with open("auto_layout.gv", "w") as f:
                f.write(rendered_string)

        rendered_graphs = pydot.graph_from_dot_data(rendered_string)
        return rendered_graphs[0]

    def apply_layout(self, diagram, rendered_graph, offset=(0, 0)):
        # NB. BB is (llx,lly,urx,ury)! (0, 0) is bottom-left!
        _, _, _, height = parse_bb(rendered_graph.get_node("graph")[0].get("bb"))

        with Transaction(self.event_manager):
            for subgraph in rendered_graph.get_subgraphs():
                id = subgraph.get_node("graph")[0].get_id().replace('"', "")
                if presentation := next(
                    (p for p in diagram.ownedPresentation if p.id == id), None
                ):
                    if bb := subgraph.get_node("graph")[0].get("bb"):
                        llx, lly, urx, ury = parse_bb(bb)
                        presentation.matrix.set(
                            x0=llx,
                            y0=height - ury,
                        )
                        presentation.width = urx - llx
                        presentation.height = ury - lly
                        presentation.request_update()
                        self.apply_layout(diagram, subgraph, offset=(llx, height - ury))

            for node in rendered_graph.get_nodes():
                if not (node.get_id() and node.get_pos()):
                    continue

                id = node.get_id().replace('"', "")
                if presentation := next(
                    (p for p in diagram.ownedPresentation if p.id == id), None
                ):
                    pos = parse_point(node.get_pos())
                    presentation.matrix.set(
                        x0=pos[0] - presentation.width / 2 - offset[0],
                        y0=height - pos[1] - presentation.height / 2 - offset[1],
                    )
                    presentation.request_update()
                    if isinstance(presentation, AttachedPresentation):
                        reconnect(
                            presentation, presentation.handles()[0], diagram.connections
                        )
            for edge in rendered_graph.get_edges():
                if not edge.get("id"):
                    continue

                id = strip_quotes(edge.get("id"))
                if presentation := next(
                    (p for p in diagram.ownedPresentation if p.id == id), None
                ):
                    presentation.orthogonal = False

                    points = parse_edge_pos(edge.get_pos())
                    segment = Segment(presentation, diagram)
                    while len(points) > len(presentation.handles()):
                        segment.split_segment(0)
                    while len(points) < len(presentation.handles()):
                        segment.merge_segment(0)

                    assert len(points) == len(presentation.handles())

                    matrix = presentation.matrix_i2c.inverse()
                    for handle, point in zip(presentation.handles(), points):
                        p = matrix.transform_point(
                            point[0] - offset[0], height - point[1] - offset[1]
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
def as_pydot(element: Element) -> pydot.Common | Iterable[pydot.Common] | None:
    return None


def diagram_as_pydot(diagram: Diagram) -> pydot.Dot:
    graph = pydot.Dot("gaphor", graph_type="graph", prog="fdp", splines="polyline")
    graph.set_pad(8 / DPI)
    for presentation in diagram.ownedPresentation:
        if presentation.parent:
            continue

        add_to_graph(graph, as_pydot(presentation))

    return graph


@as_pydot.register
def _(presentation: ElementPresentation):
    if not any(
        c for c in presentation.children if not isinstance(c, AttachedPresentation)
    ):
        for attached in presentation.children:
            if isinstance(attached, AttachedPresentation):
                yield as_pydot(attached)

        yield pydot.Node(
            presentation.id,
            id=presentation.id,
            label="",
            shape="rect",
            width=presentation.width / DPI,
            height=presentation.height / DPI,
        )
    else:
        graph = pydot.Cluster(
            presentation.id,
            id=presentation.id,
            label=presentation.subject.name
            if isinstance(presentation.subject, NamedElement)
            else "",
            margin=20,
        )

        for attached in presentation.children:
            if isinstance(attached, AttachedPresentation):
                add_to_graph(graph, as_pydot(attached))

        for child in presentation.children:
            add_to_graph(graph, as_pydot(child))

        yield graph


@as_pydot.register
def _(presentation: LinePresentation):
    connections = presentation.diagram.connections
    head_connection = connections.get_connection(presentation.head)
    tail_connection = connections.get_connection(presentation.tail)
    if (
        head_connection
        and isinstance(
            head_connection.connected, (ElementPresentation, AttachedPresentation)
        )
        and tail_connection
        and isinstance(
            tail_connection.connected, (ElementPresentation, AttachedPresentation)
        )
    ):
        return pydot.Edge(
            head_connection.connected.id,
            tail_connection.connected.id,
            id=presentation.id,
            minlen=3,
        )
    return None


@as_pydot.register
def _(presentation: AttachedPresentation):
    yield pydot.Node(
        presentation.id,
        id=presentation.id,
        label="",
        shape="rect",
        width=0.1,
        height=0.1,
    )
    handle = presentation.handles()[0]
    if connection := presentation.diagram.connections.get_connection(handle):
        yield pydot.Edge(
            connection.connected.id,
            presentation.id,
            len=0.01,
        )


@as_pydot.register
def _(presentation: ForkNodeItem):
    h1, h2 = presentation.handles()
    return pydot.Node(
        presentation.id,
        id=presentation.id,
        label="",
        shape="rect",
        width=(h2.pos.x - h1.pos.x) / DPI,
        height=(h2.pos.y - h1.pos.y) / DPI,
    )


def add_to_graph(graph, edge_or_node) -> None:
    if isinstance(edge_or_node, pydot.Edge):
        graph.add_edge(edge_or_node)
    elif isinstance(edge_or_node, pydot.Node):
        graph.add_node(edge_or_node)
    elif isinstance(edge_or_node, pydot.Graph):
        graph.add_subgraph(edge_or_node)
    elif isinstance(edge_or_node, Iterable):
        for obj in edge_or_node:
            add_to_graph(graph, obj)
    elif edge_or_node:
        raise ValueError(f"Can't transform {edge_or_node} to something DOT'ish?")


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
    return s.replace('"', "").replace("\\\n", "")
