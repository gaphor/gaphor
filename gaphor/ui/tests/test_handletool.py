"""
Test handle tool functionality.
"""

from __future__ import absolute_import

import gtk
import unittest

from gaphas.aspect import Connector, ConnectionSink
from gaphas.canvas import Context

from gaphor.UML import uml2
from gaphor.application import Application
from gaphor.diagram.actor import ActorItem
from gaphor.diagram.comment import CommentItem
from gaphor.diagram.commentline import CommentLineItem
from gaphor.ui.diagramtools import ConnectHandleTool, DiagramItemConnector

Event = Context


class DiagramItemConnectorTestCase(unittest.TestCase):
    def setUp(self):
        Application.init(
            services=['adapter_loader', 'element_factory', 'main_window', 'ui_manager', 'properties_manager',
                      'action_manager', 'properties', 'element_dispatcher'])
        self.main_window = Application.get_service('main_window')
        self.main_window.init()
        self.main_window.open()
        self.element_factory = Application.get_service('element_factory')
        self.diagram = self.element_factory.create(uml2.Diagram)
        self.comment = self.diagram.create(CommentItem,
                                           subject=self.element_factory.create(uml2.Comment))
        self.commentline = self.diagram.create(CommentLineItem)
        self.view = self.main_window.show_diagram(self.diagram).view

    def test_aspect_type(self):
        aspect = Connector(self.commentline, self.commentline.handles()[0])
        assert type(aspect) is DiagramItemConnector

    def test_query(self):
        from zope import component
        from gaphor.diagram.interfaces import IConnect
        assert component.queryMultiAdapter((self.comment, self.commentline), IConnect)

    def test_allow(self):
        aspect = Connector(self.commentline, self.commentline.handles()[0])
        assert aspect.item is self.commentline
        assert aspect.handle is self.commentline.handles()[0]

        sink = ConnectionSink(self.comment, self.comment.ports()[0])
        assert aspect.allow(sink)

    def test_connect(self):
        sink = ConnectionSink(self.comment, self.comment.ports()[0])
        aspect = Connector(self.commentline, self.commentline.handles()[0])
        aspect.connect(sink)
        canvas = self.diagram.canvas
        cinfo = canvas.get_connection(self.commentline.handles()[0])
        assert cinfo, cinfo


class HandleToolTestCase(unittest.TestCase):
    """
    Handle connection tool integration tests.
    """

    def setUp(self):
        Application.init(
            services=['adapter_loader', 'element_factory', 'main_window', 'ui_manager', 'properties_manager',
                      'action_manager', 'properties', 'element_dispatcher'])
        self.main_window = Application.get_service('main_window')
        self.main_window.open()

    def shutDown(self):
        Application.shutdown()

    def get_diagram_view(self, diagram):
        """
        Get a view for diagram.
        """
        self.main_window.show_diagram(diagram)
        view = self.main_window.get_current_diagram_view()

        # realize view, forces bounding box recalculation
        while gtk.events_pending():
            gtk.main_iteration()

        return view

    def test_iconnect(self):
        """
        Test basic glue functionality using CommentItem and CommentLine
        items.
        """
        element_factory = Application.get_service('element_factory')
        diagram = element_factory.create(uml2.Diagram)

        comment = diagram.create(CommentItem, subject=element_factory.create(uml2.Comment))
        # assert comment.height == 50
        # assert comment.width == 100

        actor = diagram.create(ActorItem, subject=element_factory.create(uml2.Actor))
        actor.matrix.translate(200, 200)
        diagram.canvas.update_matrix(actor)

        line = diagram.create(CommentLineItem)

        view = self.get_diagram_view(diagram)
        assert view, 'View should be available here'

        tool = ConnectHandleTool(view)

        # select handle:
        handle = line.handles()[-1]
        tool._grabbed_item = line
        tool._grabbed_handle = handle

        # Should glue to (238, 248)
        handle.pos = 245, 248
        item = tool.glue(line, handle, (245, 248))
        self.assertTrue(item is not None)
        self.assertEquals((238, 248), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))

        handle.pos = 245, 248
        tool.connect(line, handle, (245, 248))
        cinfo = diagram.canvas.get_connection(handle)
        self.assertTrue(cinfo.constraint is not None)
        self.assertTrue(cinfo.connected is actor, cinfo.connected)
        self.assertEquals((238, 248), view.get_matrix_i2v(line).transform_point(handle.x, handle.y))

        Connector(line, handle).disconnect()
        # tool.disconnect(line, handle)

        cinfo = diagram.canvas.get_connection(handle)

        self.assertTrue(cinfo is None)

    def test_iconnect_2(self):
        """Test connect/disconnect on comment and actor using comment-line.
        """
        element_factory = Application.get_service('element_factory')
        diagram = element_factory.create(uml2.Diagram)
        # self.main_window.show_diagram(diagram)
        comment = diagram.create(CommentItem, subject=element_factory.create(uml2.Comment))
        actor = diagram.create(ActorItem, subject=element_factory.create(uml2.Actor))
        actor.matrix.translate(200, 200)
        diagram.canvas.update_matrix(actor)
        line = diagram.create(CommentLineItem)

        view = self.get_diagram_view(diagram)

        assert view, 'View should be available here'

        tool = ConnectHandleTool(view)

        # select handle:
        handle = line.handles()[0]
        tool.grab_handle(line, handle)

        # Connect one end to the Comment
        # handle.pos = view.get_matrix_v2i(line).transform_point(45, 48)
        sink = tool.glue(line, handle, (0, 0))
        assert sink is not None
        assert sink.item is comment

        tool.connect(line, handle, (0, 0))
        cinfo = diagram.canvas.get_connection(handle)
        self.assertTrue(cinfo is not None, None)
        self.assertTrue(cinfo.item is line)
        self.assertTrue(cinfo.connected is comment)

        pos = view.get_matrix_i2v(line).transform_point(handle.x, handle.y)
        self.assertAlmostEquals(0, pos[0], 0.00001)
        self.assertAlmostEquals(0, pos[1], 0.00001)

        # Connect the other end to the actor:
        handle = line.handles()[-1]
        tool.grab_handle(line, handle)

        handle.pos = 140, 150
        sink = tool.glue(line, handle, (200, 200))
        self.assertTrue(sink.item is actor)
        tool.connect(line, handle, (200, 200))

        cinfo = view.canvas.get_connection(handle)
        self.assertTrue(cinfo.item is line)
        self.assertTrue(cinfo.connected is actor)

        self.assertEquals((200, 200), view.get_matrix_i2v(line).transform_point(handle.x, handle.y))

        # Try to connect far away from any item will only do a full disconnect
        self.assertEquals(len(comment.subject.annotatedElement), 1, comment.subject.annotatedElement)
        self.assertTrue(actor.subject in comment.subject.annotatedElement)

        sink = tool.glue(line, handle, (500, 500))
        self.assertTrue(sink is None, sink)
        tool.connect(line, handle, (500, 500))

        self.assertEquals((200, 200), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        cinfo = view.canvas.get_connection(handle)
        self.assertTrue(cinfo is None)

    def skiptest_connect_3(self):
        """Test connecting through events (button press/release, motion).
        """
        element_factory = Application.get_service('element_factory')
        diagram = element_factory.create(uml2.Diagram)

        comment = diagram.create(CommentItem, subject=element_factory.create(uml2.Comment))
        # self.assertEquals(30, comment.height)
        # self.assertEquals(100, comment.width)

        actor = diagram.create(ActorItem, subject=element_factory.create(uml2.Actor))
        actor.matrix.translate(200, 200)
        diagram.canvas.update_matrix(actor)
        # assert actor.height == 60, actor.height
        # assert actor.width == 38, actor.width

        line = diagram.create(CommentLineItem)
        assert line.handles()[0].pos, (0.0, 0.0)
        assert line.handles()[-1].pos, (10.0, 10.0)

        view = self.get_diagram_view(diagram)
        assert view, 'View should be available here'

        tool = ConnectHandleTool(view)

        tool.on_button_press(Event(x=0, y=0, state=0))
        tool.on_button_release(Event(x=0, y=0, state=0))

        handle = line.handles()[0]
        self.assertEquals((.0, .0), view.canvas.get_matrix_i2c(line).transform_point(*handle.pos))
        cinfo = diagram.canvas.get_connection(handle)
        self.assertTrue(cinfo.connected is comment)
        # self.assertTrue(handle.connected_to is comment, 'c = ' + str(handle.connected_to))
        # self.assertTrue(handle.connection_data is not None)

        # Grab the second handle and drag it to the actor

        tool.on_button_press(Event(x=10, y=10, state=0))
        tool.on_motion_notify(Event(x=200, y=200, state=0xffff))
        tool.on_button_release(Event(x=200, y=200, state=0))

        handle = line.handles()[-1]
        self.assertEquals((200, 200), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        cinfo = diagram.canvas.get_connection(handle)
        self.assertTrue(cinfo.connected is actor)
        # self.assertTrue(handle.connection_data is not None)
        self.assertTrue(actor.subject in comment.subject.annotatedElement)

        # Press, release, nothing should change

        tool.on_button_press(Event(x=200, y=200, state=0))
        tool.on_motion_notify(Event(x=200, y=200, state=0xffff))
        tool.on_button_release(Event(x=200, y=200, state=0))

        handle = line.handles()[-1]
        self.assertEquals((200, 200), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        cinfo = diagram.canvas.get_connection(handle)
        self.assertTrue(cinfo.connected is actor)
        # self.assertTrue(handle.connection_data is not None)
        self.assertTrue(actor.subject in comment.subject.annotatedElement)

        # Move second handle away from the actor. Should remove connection

        tool.on_button_press(Event(x=200, y=200, state=0))
        tool.on_motion_notify(Event(x=500, y=500, state=0xffff))
        tool.on_button_release(Event(x=500, y=500, state=0))

        handle = line.handles()[-1]
        self.assertEquals((500, 500), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        cinfo = diagram.canvas.get_connection(handle)
        self.assertTrue(cinfo is None)
        # self.assertTrue(handle.connection_data is None)
        self.assertEquals(len(comment.subject.annotatedElement), 0)

# vim:sw=4:et:ai
