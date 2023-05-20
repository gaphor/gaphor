"""Test handle tool functionality."""

import pytest
from gaphas.connector import ConnectionSink
from gaphas.connector import Connector as ConnectorAspect
from gaphas.handlemove import HandleMove
from gi.repository import GLib, Gtk

from gaphor import UML
from gaphor.core.modeling import Comment, Diagram
from gaphor.diagram._connector import PresentationConnector
from gaphor.diagram.connectors import Connector
from gaphor.diagram.event import DiagramOpened
from gaphor.diagram.general.comment import CommentItem
from gaphor.diagram.general.commentline import CommentLineItem
from gaphor.ui.diagrams import Diagrams
from gaphor.ui.toolbox import Toolbox
from gaphor.UML.usecases.actor import ActorItem


@pytest.fixture
def diagrams(event_manager, element_factory, modeling_language, properties):
    toolbox = Toolbox(event_manager, properties, modeling_language)
    diagrams = Diagrams(
        event_manager, element_factory, properties, modeling_language, toolbox
    )
    window = Gtk.Window.new()
    box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
    window.set_child(box)
    box.append(diagrams.open())
    window.set_visible(True)
    yield diagrams
    diagrams.close()


@pytest.fixture
def connections(diagram):
    return diagram.connections


@pytest.fixture
def comment(element_factory, diagram):
    return diagram.create(CommentItem, subject=element_factory.create(Comment))


@pytest.fixture
def commentline(diagram):
    return diagram.create(CommentLineItem)


def test_aspect_type(commentline, connections):
    aspect = ConnectorAspect(commentline, commentline.handles()[0], connections)
    assert isinstance(aspect, PresentationConnector)


def test_query(comment, commentline):
    assert Connector(comment, commentline)


def test_allow(commentline, comment, connections):
    aspect = ConnectorAspect(commentline, commentline.handles()[0], connections)
    assert aspect.item is commentline
    assert aspect.handle is commentline.handles()[0]

    sink = ConnectionSink(comment)
    assert aspect.allow(sink)


def test_connect(diagram, comment, commentline, connections):
    sink = ConnectionSink(comment)
    aspect = ConnectorAspect(commentline, commentline.handles()[0], connections)
    aspect.connect(sink)
    cinfo = diagram.connections.get_connection(commentline.handles()[0])
    assert cinfo, cinfo


def current_diagram_view(diagrams):
    """Get a view for the current diagram."""
    view = diagrams.get_current_view()

    # realize view, forces bounding box recalculation
    ctx = GLib.main_context_default()
    while ctx.pending():
        ctx.iteration(False)

    return view


def test_iconnect(event_manager, element_factory, diagrams):
    """Test basic glue functionality using CommentItem and CommentLine
    items."""
    diagram = element_factory.create(Diagram)
    event_manager.handle(DiagramOpened(diagram))
    comment = diagram.create(CommentItem, subject=element_factory.create(Comment))

    line = diagram.create(CommentLineItem)

    view = current_diagram_view(diagrams)
    assert view, "View should be available here"

    # select handle:
    handle = line.handles()[-1]

    move = HandleMove(line, handle, view)
    handle.pos = (0, 0)
    item = move.glue(handle.pos)
    assert item is not None

    move.connect(handle.pos)
    cinfo = diagram.connections.get_connection(handle)
    assert cinfo.constraint is not None
    assert cinfo.connected is comment, cinfo.connected

    ConnectorAspect(line, handle, diagram.connections).disconnect()

    cinfo = diagram.connections.get_connection(handle)

    assert cinfo is None


def test_connect_comment_and_actor(event_manager, element_factory, diagrams):
    """Test connect/disconnect on comment and actor using comment-line."""
    diagram = element_factory.create(Diagram)
    event_manager.handle(DiagramOpened(diagram))
    comment = diagram.create(CommentItem, subject=element_factory.create(Comment))

    line = diagram.create(CommentLineItem)

    view = current_diagram_view(diagrams)
    assert view, "View should be available here"

    handle = line.handles()[0]
    move = HandleMove(line, handle, view)

    handle.pos = (0, 0)
    sink = move.glue(handle.pos)
    assert sink is not None
    assert sink.item is comment

    move.connect(handle.pos)
    cinfo = diagram.connections.get_connection(handle)
    assert cinfo is not None, None
    assert cinfo.item is line
    assert cinfo.connected is comment

    # Connect the other end to the Actor:
    actor = diagram.create(ActorItem, subject=element_factory.create(UML.Actor))

    handle = line.handles()[-1]
    move = HandleMove(line, handle, view)

    handle.pos = (0, 0)
    sink = move.glue(handle.pos)
    assert sink, f"No sink at {handle.pos}"
    assert sink.item is actor
    move.connect(handle.pos)

    cinfo = view.model.connections.get_connection(handle)
    assert cinfo.item is line
    assert cinfo.connected is actor

    # Try to connect far away from any item will only do a full disconnect
    assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
    assert actor.subject in comment.subject.annotatedElement

    sink = move.glue((500, 500))
    assert sink is None, sink
    move.connect((500, 500))

    cinfo = view.model.connections.get_connection(handle)
    assert cinfo is None
