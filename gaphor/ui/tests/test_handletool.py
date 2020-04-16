"""
Test handle tool functionality.
"""

import pytest
from gaphas.aspect import ConnectionSink
from gaphas.aspect import Connector as ConnectorAspect
from gi.repository import Gdk, Gtk

from gaphor import UML
from gaphor.diagram.connectors import Connector
from gaphor.diagram.diagramtools import ConnectHandleTool, DiagramItemConnector
from gaphor.diagram.general.comment import CommentItem
from gaphor.diagram.general.commentline import CommentLineItem
from gaphor.services.componentregistry import ComponentRegistry
from gaphor.ui.abc import UIComponent
from gaphor.ui.event import DiagramOpened
from gaphor.ui.mainwindow import Diagrams
from gaphor.UML.modelinglanguage import UMLModelingLanguage
from gaphor.UML.usecases.actor import ActorItem


@pytest.fixture
def diagrams(event_manager, element_factory, properties):
    window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
    diagrams = Diagrams(
        event_manager, element_factory, properties, UMLModelingLanguage()
    )
    window.add(diagrams.open())
    window.show()
    yield diagrams
    diagrams.close()


@pytest.fixture
def comment(element_factory, diagram):
    return diagram.create(CommentItem, subject=element_factory.create(UML.Comment))


@pytest.fixture
def commentline(diagram):
    return diagram.create(CommentLineItem)


def test_aspect_type(commentline):
    aspect = ConnectorAspect(commentline, commentline.handles()[0])
    assert isinstance(aspect, DiagramItemConnector)


def test_query(comment, commentline):
    assert Connector(comment, commentline)


def test_allow(commentline, comment):
    aspect = ConnectorAspect(commentline, commentline.handles()[0])
    assert aspect.item is commentline
    assert aspect.handle is commentline.handles()[0]

    sink = ConnectionSink(comment, comment.ports()[0])
    assert aspect.allow(sink)


def test_connect(diagram, comment, commentline):
    sink = ConnectionSink(comment, comment.ports()[0])
    aspect = ConnectorAspect(commentline, commentline.handles()[0])
    aspect.connect(sink)
    canvas = diagram.canvas
    cinfo = canvas.get_connection(commentline.handles()[0])
    assert cinfo, cinfo


def current_diagram_view(diagrams):
    """
    Get a view for the current diagram.
    """
    view = diagrams.get_current_view()

    # realize view, forces bounding box recalculation
    while Gtk.events_pending():
        Gtk.main_iteration()

    return view


def test_iconnect(event_manager, element_factory, diagrams):
    """
    Test basic glue functionality using CommentItem and CommentLine
    items.
    """
    diagram = element_factory.create(UML.Diagram)
    event_manager.handle(DiagramOpened(diagram))
    comment = diagram.create(CommentItem, subject=element_factory.create(UML.Comment))

    actor = diagram.create(ActorItem, subject=element_factory.create(UML.Actor))
    actor.matrix.translate(200, 200)
    diagram.canvas.update_matrix(actor)

    line = diagram.create(CommentLineItem)

    view = current_diagram_view(diagrams)
    assert view, "View should be available here"
    comment_bb = view.get_item_bounding_box(comment)

    # select handle:
    handle = line.handles()[-1]
    tool = ConnectHandleTool(view=view)

    tool.grab_handle(line, handle)
    handle.pos = (comment_bb.x, comment_bb.y)
    item = tool.glue(line, handle, handle.pos)
    assert item is not None

    tool.connect(line, handle, handle.pos)
    cinfo = diagram.canvas.get_connection(handle)
    assert cinfo.constraint is not None
    assert cinfo.connected is actor, cinfo.connected

    ConnectorAspect(line, handle).disconnect()

    cinfo = diagram.canvas.get_connection(handle)

    assert cinfo is None


def test_connect_comment_and_actor(event_manager, element_factory, diagrams):
    """Test connect/disconnect on comment and actor using comment-line.
    """
    diagram = element_factory.create(UML.Diagram)
    event_manager.handle(DiagramOpened(diagram))
    comment = diagram.create(CommentItem, subject=element_factory.create(UML.Comment))

    line = diagram.create(CommentLineItem)

    view = current_diagram_view(diagrams)
    assert view, "View should be available here"

    tool = ConnectHandleTool(view)

    # Connect one end to the Comment:
    handle = line.handles()[0]
    tool.grab_handle(line, handle)

    handle.pos = (0, 0)
    sink = tool.glue(line, handle, handle.pos)
    assert sink is not None
    assert sink.item is comment

    tool.connect(line, handle, handle.pos)
    cinfo = diagram.canvas.get_connection(handle)
    assert cinfo is not None, None
    assert cinfo.item is line
    assert cinfo.connected is comment

    # Connect the other end to the Actor:
    actor = diagram.create(ActorItem, subject=element_factory.create(UML.Actor))

    handle = line.handles()[-1]
    tool.grab_handle(line, handle)

    handle.pos = (0, 0)
    sink = tool.glue(line, handle, handle.pos)
    assert sink, f"No sink at {handle.pos}"
    assert sink.item is actor
    tool.connect(line, handle, handle.pos)

    cinfo = view.canvas.get_connection(handle)
    assert cinfo.item is line
    assert cinfo.connected is actor

    # Try to connect far away from any item will only do a full disconnect
    assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
    assert actor.subject in comment.subject.annotatedElement

    sink = tool.glue(line, handle, (500, 500))
    assert sink is None, sink
    tool.connect(line, handle, (500, 500))

    cinfo = view.canvas.get_connection(handle)
    assert cinfo is None
