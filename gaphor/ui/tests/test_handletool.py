"""
Test handle tool functionality.
"""

import unittest
import pytest

from gaphas.aspect import Connector, ConnectionSink
from gi.repository import Gdk, Gtk

from gaphor import UML
from gaphor.application import Application
from gaphor.diagram.usecases.actor import ActorItem
from gaphor.diagram.general.comment import CommentItem
from gaphor.diagram.general.commentline import CommentLineItem
from gaphor.diagram.connectors import IConnect
from gaphor.ui.diagramtools import ConnectHandleTool, DiagramItemConnector
from gaphor.ui.event import DiagramShow
from gaphor.ui.abc import UIComponent


@pytest.fixture
def application():
    Application.init(
        services=[
            "event_manager",
            "component_registry",
            "element_factory",
            "main_window",
            "properties_manager",
            "properties",
            "namespace",
            "diagrams",
            "toolbox",
            "elementeditor",
            "import_menu",
            "export_menu",
            "tools_menu",
        ]
    )
    main_window = Application.get_service("main_window")
    main_window.open()
    yield Application
    Application.shutdown()


@pytest.fixture
def element_factory(application):
    return application.get_service("element_factory")


@pytest.fixture
def event_manager(application):
    return application.get_service("event_manager")


@pytest.fixture
def diagram(element_factory):
    return element_factory.create(UML.Diagram)


@pytest.fixture
def comment(element_factory, diagram):
    return diagram.create(CommentItem, subject=element_factory.create(UML.Comment))


@pytest.fixture
def commentline(diagram):
    return diagram.create(CommentLineItem)


def test_aspect_type(commentline):
    aspect = Connector(commentline, commentline.handles()[0])
    assert isinstance(aspect, DiagramItemConnector)


def test_query(comment):
    assert IConnect(comment, commentline)


def test_allow(commentline, comment):
    aspect = Connector(commentline, commentline.handles()[0])
    assert aspect.item is commentline
    assert aspect.handle is commentline.handles()[0]

    sink = ConnectionSink(comment, comment.ports()[0])
    assert aspect.allow(sink)


def test_connect(diagram, comment, commentline):
    sink = ConnectionSink(comment, comment.ports()[0])
    aspect = Connector(commentline, commentline.handles()[0])
    aspect.connect(sink)
    canvas = diagram.canvas
    cinfo = canvas.get_connection(commentline.handles()[0])
    assert cinfo, cinfo


class HandleToolTestCase(unittest.TestCase):
    """
    Handle connection tool integration tests.
    """

    def setUp(self):
        Application.init(
            services=[
                "event_manager",
                "component_registry",
                "element_factory",
                "main_window",
                "properties_manager",
                "properties",
                "namespace",
                "diagrams",
                "toolbox",
                "elementeditor",
                "import_menu",
                "export_menu",
                "tools_menu",
            ]
        )
        self.component_registry = Application.get_service("component_registry")
        self.event_manager = Application.get_service("event_manager")

        self.main_window = Application.get_service("main_window")
        self.main_window.open()

    def shutDown(self):
        Application.shutdown()

    def get_diagram_view(self, diagram):
        """
        Get a view for diagram.
        """
        view = self.component_registry.get(UIComponent, "diagrams").get_current_view()

        # realize view, forces bounding box recalculation
        while Gtk.events_pending():
            Gtk.main_iteration()

        return view

    def test_iconnect(self):
        """
        Test basic glue functionality using CommentItem and CommentLine
        items.
        """
        element_factory = Application.get_service("element_factory")
        diagram = element_factory.create(UML.Diagram)
        self.event_manager.handle(DiagramShow(diagram))
        comment = diagram.create(
            CommentItem, subject=element_factory.create(UML.Comment)
        )

        actor = diagram.create(ActorItem, subject=element_factory.create(UML.Actor))
        actor.matrix.translate(200, 200)
        diagram.canvas.update_matrix(actor)

        line = diagram.create(CommentLineItem)

        view = self.get_diagram_view(diagram)
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

        Connector(line, handle).disconnect()

        cinfo = diagram.canvas.get_connection(handle)

        assert cinfo is None

    def test_connect_comment_and_actor(self):
        """Test connect/disconnect on comment and actor using comment-line.
        """
        element_factory = Application.get_service("element_factory")
        diagram = element_factory.create(UML.Diagram)
        self.event_manager.handle(DiagramShow(diagram))
        comment = diagram.create(
            CommentItem, subject=element_factory.create(UML.Comment)
        )

        line = diagram.create(CommentLineItem)

        view = self.get_diagram_view(diagram)
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
        self.assertEqual(
            len(comment.subject.annotatedElement), 1, comment.subject.annotatedElement
        )
        assert actor.subject in comment.subject.annotatedElement

        sink = tool.glue(line, handle, (500, 500))
        assert sink is None, sink
        tool.connect(line, handle, (500, 500))

        cinfo = view.canvas.get_connection(handle)
        assert cinfo is None

    def skiptest_connect_3(self):
        """Test connecting through events (button press/release, motion).
        """
        element_factory = Application.get_service("element_factory")
        diagram = element_factory.create(UML.Diagram)

        comment = diagram.create(
            CommentItem, subject=element_factory.create(UML.Comment)
        )
        # self.assertEqual(30, comment.height)
        # self.assertEqual(100, comment.width)

        actor = diagram.create(ActorItem, subject=element_factory.create(UML.Actor))
        actor.matrix.translate(200, 200)
        diagram.canvas.update_matrix(actor)
        # assert actor.height == 60, actor.height
        # assert actor.width == 38, actor.width

        line = diagram.create(CommentLineItem)
        assert line.handles()[0].pos, (0.0, 0.0)
        assert line.handles()[-1].pos, (10.0, 10.0)

        view = self.get_diagram_view(diagram)
        assert view, "View should be available here"

        tool = ConnectHandleTool(view)

        tool.on_button_press(Gdk.Event(x=0, y=0, state=0))
        tool.on_button_release(Gdk.Event(x=0, y=0, state=0))

        handle = line.handles()[0]
        assert (0.0, 0.0) == view.canvas.get_matrix_i2c(line).transform_point(
            *handle.pos
        )
        cinfo = diagram.canvas.get_connection(handle)
        assert cinfo.connected is comment
        # self.assertTrue(handle.connected_to is comment, 'c = ' + str(handle.connected_to))
        # self.assertTrue(handle.connection_data is not None)

        # Grab the second handle and drag it to the actor

        tool.on_button_press(Gdk.Event(x=10, y=10, state=0))
        tool.on_motion_notify(Gdk.Event(x=200, y=200, state=0xFFFF))
        tool.on_button_release(Gdk.Event(x=200, y=200, state=0))

        handle = line.handles()[-1]
        assert (200, 200) == view.canvas.get_matrix_i2c(line).transform_point(
            handle.x, handle.y
        )
        cinfo = diagram.canvas.get_connection(handle)
        assert cinfo.connected is actor
        # self.assertTrue(handle.connection_data is not None)
        self.assertTrue(actor.subject in comment.subject.annotatedElement)

        # Press, release, nothing should change

        tool.on_button_press(Gdk.Event(x=200, y=200, state=0))
        tool.on_motion_notify(Gdk.Event(x=200, y=200, state=0xFFFF))
        tool.on_button_release(Gdk.Event(x=200, y=200, state=0))

        handle = line.handles()[-1]
        assert (200, 200) == view.canvas.get_matrix_i2c(line).transform_point(
            handle.x, handle.y
        )
        cinfo = diagram.canvas.get_connection(handle)
        assert cinfo.connected is actor
        # self.assertTrue(handle.connection_data is not None)
        self.assertTrue(actor.subject in comment.subject.annotatedElement)

        # Move second handle away from the actor. Should remove connection

        tool.on_button_press(Gdk.Event(x=200, y=200, state=0))
        tool.on_motion_notify(Gdk.Event(x=500, y=500, state=0xFFFF))
        tool.on_button_release(Gdk.Event(x=500, y=500, state=0))

        handle = line.handles()[-1]
        assert (500, 500) == view.canvas.get_matrix_i2c(line).transform_point(
            handle.x, handle.y
        )
        cinfo = diagram.canvas.get_connection(handle)
        assert cinfo is None
        # self.assertTrue(handle.connection_data is None)
        self.assertEqual(len(comment.subject.annotatedElement), 0)
