"""
Test handle tool functionality.
"""

import unittest
from gaphor import UML
from gaphor.diagram.comment import CommentItem
from gaphor.diagram.commentline import CommentLineItem
from gaphor.diagram.actor import ActorItem
from gaphor.ui.diagramtools import ConnectHandleTool
from gaphas.canvas import Context

from gaphor.application import Application

Event = Context


class HandleToolTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(services=['adapter_loader', 'element_factory', 'gui_manager', 'properties_manager'])
        self.main_window = Application.get_service('gui_manager').main_window

    def shutDown(self):
        Application.shutdown()

    def test_iconnect(self):
        """
        Test basic glue functionality using CommentItem and CommentLine
        items.
        """
        element_factory = Application.get_service('element_factory')
        diagram = element_factory.create(UML.Diagram)
        #self.main_window.show_diagram(diagram)
        comment = diagram.create(CommentItem, subject=element_factory.create(UML.Comment))
        assert comment.height == 50
        assert comment.width == 100
        actor = diagram.create(ActorItem, subject=element_factory.create(UML.Actor))
        line = diagram.create(CommentLineItem)
        tool = ConnectHandleTool()

        self.main_window.show_diagram(diagram)
        view = self.main_window.get_current_diagram_view()
        assert view, 'View should be available here'

        # select handle:
        handle = line.handles()[-1]
        tool._grabbed_item = line
        tool._grabbed_handle = handle

        # Should glue to (45, 50)
        handle.pos = 45, 48
        tool.glue(view, line, handle, 45, 48)

        self.assertEquals((45, 50), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))

        handle.x, handle.y = 45, 48
        tool.connect(view, line, handle, 45, 48)
        self.assertEquals((45, 50), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        assert handle.connected_to is actor, handle.connected_to
        assert handle._connect_constraint is not None

        tool.disconnect(view, line, handle)
        
        assert handle.connected_to is actor
        assert handle._connect_constraint is None


    def test_iconnect_2(self):
        """Test connect/disconnect on comment and actor using comment-line.
        """
        element_factory = Application.get_service('element_factory')
        diagram = element_factory.create(UML.Diagram)
        #self.main_window.show_diagram(diagram)
        comment = diagram.create(CommentItem, subject=element_factory.create(UML.Comment))
        assert comment.height == 50
        assert comment.width == 100
        actor = diagram.create(ActorItem, subject=element_factory.create(UML.Actor))
        actor.matrix.translate(200, 200)
        diagram.canvas.update_matrix(actor)
        #print diagram.canvas.get_matrix_i2c(actor), actor.matrix
        assert actor.height == 60, actor.height
        assert actor.width == 38, actor.width
        line = diagram.create(CommentLineItem)
        tool = ConnectHandleTool()

        self.main_window.show_diagram(diagram)
        view = self.main_window.get_current_diagram_view()
        assert view, 'View should be available here'

        # select handle:
        handle = line.handles()[0]
        tool.grab_handle(line, handle)

        # Connect one end to the Comment
        handle.x, handle.y = 45, 48
        tool.connect(view, line, handle, 45, 48)
        self.assertEquals((45, 50), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        assert handle.connected_to is comment, handle.connected_to
        assert handle._connect_constraint is not None

        # Connect the other end to the actor:

        handle = line.handles()[-1]
        tool.grab_handle(line, handle)

        handle.x, handle.y = 140, 150
        assert tool.glue(view, line, handle, 200, 200) is actor
        tool.connect(view, line, handle, 200, 200)
        self.assertEquals((200, 200), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        assert handle.connected_to is actor, handle.connected_to
        assert handle._connect_constraint is not None
        
        # Disconnect only disconnects the constraints:

        assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
        assert actor.subject in comment.subject.annotatedElement
       
        tool.disconnect(view, line, handle)

        self.assertEquals((200, 200), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        assert handle.connected_to is actor, handle.connected_to
        assert handle._connect_constraint is None

        # Try to connect far away from any item will only do a full disconnect

        assert len(comment.subject.annotatedElement) == 1, comment.subject.annotatedElement
        assert actor.subject in comment.subject.annotatedElement

        assert tool.glue(view, line, handle, 500, 500) is None
        tool.connect(view, line, handle, 500, 500)

        self.assertEquals((200, 200), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        assert handle.connected_to is None, handle.connected_to
        assert handle._connect_constraint is None


    def test_connect_3(self):
        """Test connecting through events (button press/release, motion).
        """
        element_factory = Application.get_service('element_factory')
        diagram = element_factory.create(UML.Diagram)
        #self.main_window.show_diagram(diagram)
        comment = diagram.create(CommentItem, subject=element_factory.create(UML.Comment))
        assert comment.height == 50
        assert comment.width == 100
        actor = diagram.create(ActorItem, subject=element_factory.create(UML.Actor))
        actor.matrix.translate(200, 200)
        diagram.canvas.update_matrix(actor)
        #print diagram.canvas.get_matrix_i2c(actor), actor.matrix
        assert actor.height == 60, actor.height
        assert actor.width == 38, actor.width
        line = diagram.create(CommentLineItem)
        assert line.handles()[0].pos, (0.0, 0.0)
        assert line.handles()[-1].pos, (10.0, 10.0)
        tool = ConnectHandleTool()

        self.main_window.show_diagram(diagram)
        view = self.main_window.get_current_diagram_view()
        assert view, 'View should be available here'

        # Add extra methods so the Context can impersonate a ToolChainContext
        def dummy_grab(): pass
        context = Context(view=view, grab=dummy_grab, ungrab=dummy_grab)

        tool.on_button_press(context, Event(x=0, y=0, state=0))
        tool.on_button_release(context, Event(x=0, y=0, state=0))

        handle = line.handles()[0]
        self.assertEquals((0, 0), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        assert handle.connected_to is comment, 'c =' + str(handle.connected_to)
        assert handle._connect_constraint is not None

        # Grab the second handle and drag it to the actor

        tool.on_button_press(context, Event(x=10, y=10, state=0))
        tool.on_motion_notify(context, Event(x=200, y=200, state=0xffff))
        tool.on_button_release(context, Event(x=200, y=200, state=0))

        handle = line.handles()[-1]
        self.assertEquals((200, 200), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        assert handle.connected_to is actor
        assert handle._connect_constraint is not None
        assert actor.subject in comment.subject.annotatedElement

        # Press, release, nothing should change

        tool.on_button_press(context, Event(x=200, y=200, state=0))
        tool.on_motion_notify(context, Event(x=200, y=200, state=0xffff))
        tool.on_button_release(context, Event(x=200, y=200, state=0))

        handle = line.handles()[-1]
        self.assertEquals((200, 200), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        assert handle.connected_to is actor
        assert handle._connect_constraint is not None
        assert actor.subject in comment.subject.annotatedElement

        # Move second handle away from the actor. Should remove connection

        tool.on_button_press(context, Event(x=200, y=200, state=0))
        tool.on_motion_notify(context, Event(x=500, y=500, state=0xffff))
        tool.on_button_release(context, Event(x=500, y=500, state=0))

        handle = line.handles()[-1]
        self.assertEquals((500, 500), view.canvas.get_matrix_i2c(line).transform_point(handle.x, handle.y))
        assert handle.connected_to is None
        assert handle._connect_constraint is None
        assert len(comment.subject.annotatedElement) == 0


# vim:sw=4:et:ai
