"""
Test handle tool functionality.
"""

import unittest
import gtk

from gaphor import UML
from gaphor.diagram.comment import CommentItem
from gaphor.diagram.commentline import CommentLineItem
from gaphor.diagram.actor import ActorItem
from gaphor.ui.diagramtools import ConnectHandleTool
from gaphas.canvas import Context

from gaphor.application import Application

Event = Context


class HandleToolTestCase(unittest.TestCase):
    """
    Handle connection tool integration tests.
    """

    def setUp(self):
        Application.init(services=['adapter_loader', 'element_factory', 'gui_manager', 'properties_manager', 'action_manager', 'properties', 'property_based_dispatcher'])
        self.main_window = Application.get_service('gui_manager').main_window

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
        diagram = element_factory.create(UML.Diagram)

        comment = diagram.create(CommentItem, subject=element_factory.create(UML.Comment))
        assert comment.height == 50
        assert comment.width == 100

        actor = diagram.create(ActorItem, subject=element_factory.create(UML.Actor))
        actor.matrix.translate(200, 200)
        diagram.canvas.update_matrix(actor)

        line = diagram.create(CommentLineItem)
        tool = ConnectHandleTool()

        view = self.get_diagram_view(diagram)
        assert view, 'View should be available here'

        # select handle:
        handle = line.handles()[-1]
        tool._grabbed_item = line
        tool._grabbed_handle = handle

        # Should glue to (238, 248)
        handle.pos = 245, 248
        item = tool.glue(view, line, handle, (245, 248))
        self.assertTrue(item is not None)
        self.assertEquals((238, 248), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))

        handle.x, handle.y = 245, 248
        tool.connect(view, line, handle, (245, 248))
        self.assertTrue(handle.connection_data is not None)
        self.assertTrue(handle.connected_to is actor, handle.connected_to)
        self.assertEquals((238, 248), view.get_matrix_i2v(line).transform_point(handle.x, handle.y))

        tool.disconnect(view, line, handle)
        
        self.assertTrue(handle.connected_to is None)
        self.assertTrue(handle.connection_data is None)


    def test_iconnect_2(self):
        """Test connect/disconnect on comment and actor using comment-line.
        """
        element_factory = Application.get_service('element_factory')
        diagram = element_factory.create(UML.Diagram)
        #self.main_window.show_diagram(diagram)
        comment = diagram.create(CommentItem, subject=element_factory.create(UML.Comment))
        assert comment.width == 100
        assert comment.height == 50

        actor = diagram.create(ActorItem, subject=element_factory.create(UML.Actor))
        actor.matrix.translate(200, 200)
        diagram.canvas.update_matrix(actor)
        #print diagram.canvas.get_matrix_i2c(actor), actor.matrix
        assert actor.width == 38, actor.width
        assert actor.height == 60, actor.height
        line = diagram.create(CommentLineItem)
        tool = ConnectHandleTool()

        view = self.get_diagram_view(diagram)

        assert view, 'View should be available here'

        # select handle:
        handle = line.handles()[0]
        tool.grab_handle(line, handle)

        # Connect one end to the Comment
        handle.pos = view.get_matrix_v2i(line).transform_point(45, 48)
        tool.connect(view, line, handle, (45, 48))
        self.assertTrue(hasattr(handle, 'connection_data'))
        self.assertTrue(handle.connection_data is not None)
        self.assertTrue(handle.connected_to is comment)
        pos = view.get_matrix_i2v(line).transform_point(handle.x, handle.y)
        self.assertAlmostEquals(45, pos[0], 0.00001)
        self.assertAlmostEquals(50, pos[1], 0.00001)

        # Connect the other end to the actor:
        handle = line.handles()[-1]
        tool.grab_handle(line, handle)

        handle.x, handle.y = 140, 150
        glued, port = tool.glue(view, line, handle, (200, 200))
        self.assertTrue(glued is actor)
        tool.connect(view, line, handle, (200, 200))
        self.assertTrue(hasattr(handle, 'connection_data'))
        self.assertTrue(handle.connection_data is not None)
        self.assertTrue(handle.connected_to is actor)
        self.assertEquals((200, 200), view.get_matrix_i2v(line).transform_point(handle.x, handle.y))
        
        # Try to connect far away from any item will only do a full disconnect
        self.assertEquals(len(comment.subject.annotatedElement), 1, comment.subject.annotatedElement)
        self.assertTrue(actor.subject in comment.subject.annotatedElement)

        item, port = tool.glue(view, line, handle, (500, 500))
        self.assertTrue(item is None, item)
        self.assertTrue(port is None, port)
        tool.connect(view, line, handle, (500, 500))

        self.assertEquals((200, 200), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        self.assertTrue(handle.connected_to is None)
        self.assertTrue(handle.connection_data is None)


    def test_connect_3(self):
        """Test connecting through events (button press/release, motion).
        """
        element_factory = Application.get_service('element_factory')
        diagram = element_factory.create(UML.Diagram)

        comment = diagram.create(CommentItem, subject=element_factory.create(UML.Comment))
        assert comment.height == 50
        assert comment.width == 100

        actor = diagram.create(ActorItem, subject=element_factory.create(UML.Actor))
        actor.matrix.translate(200, 200)
        diagram.canvas.update_matrix(actor)
        assert actor.height == 60, actor.height
        assert actor.width == 38, actor.width

        line = diagram.create(CommentLineItem)
        assert line.handles()[0].pos, (0.0, 0.0)
        assert line.handles()[-1].pos, (10.0, 10.0)
        tool = ConnectHandleTool()

        view = self.get_diagram_view(diagram)
        assert view, 'View should be available here'

        # Add extra methods so the Context can impersonate a ToolChainContext
        def dummy_grab(): pass
        context = Context(view=view, grab=dummy_grab, ungrab=dummy_grab)

        tool.on_button_press(context, Event(x=0, y=0, state=0))
        tool.on_button_release(context, Event(x=0, y=0, state=0))

        handle = line.handles()[0]
        self.assertEquals((0, 0), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        self.assertTrue(handle.connected_to is comment, 'c = ' + str(handle.connected_to))
        self.assertTrue(handle.connection_data is not None)

        # Grab the second handle and drag it to the actor

        tool.on_button_press(context, Event(x=10, y=10, state=0))
        tool.on_motion_notify(context, Event(x=200, y=200, state=0xffff))
        tool.on_button_release(context, Event(x=200, y=200, state=0))

        handle = line.handles()[-1]
        self.assertEquals((200, 200), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        self.assertTrue(handle.connected_to is actor)
        self.assertTrue(handle.connection_data is not None)
        self.assertTrue(actor.subject in comment.subject.annotatedElement)

        # Press, release, nothing should change

        tool.on_button_press(context, Event(x=200, y=200, state=0))
        tool.on_motion_notify(context, Event(x=200, y=200, state=0xffff))
        tool.on_button_release(context, Event(x=200, y=200, state=0))

        handle = line.handles()[-1]
        self.assertEquals((200, 200), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        self.assertTrue(handle.connected_to is actor)
        self.assertTrue(handle.connection_data is not None)
        self.assertTrue(actor.subject in comment.subject.annotatedElement)

        # Move second handle away from the actor. Should remove connection

        tool.on_button_press(context, Event(x=200, y=200, state=0))
        tool.on_motion_notify(context, Event(x=500, y=500, state=0xffff))
        tool.on_button_release(context, Event(x=500, y=500, state=0))

        handle = line.handles()[-1]
        self.assertEquals((500, 500), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        self.assertTrue(handle.connected_to is None)
        self.assertTrue(handle.connection_data is None)
        self.assertEquals(len(comment.subject.annotatedElement), 0)


# vim:sw=4:et:ai
