"""
Test handle tool functionality.
"""

import unittest
from gaphor import resource
from gaphor import UML
from gaphor.ui.mainwindow import MainWindow
from gaphor.diagram import CommentItem, CommentLineItem
from gaphor.diagram.tool import ConnectHandleTool
from gaphor.diagram.interfaces import IConnect


class HandleToolTestCase(unittest.TestCase):

    main_window = resource(MainWindow)
    main_window.construct()

    def test_glue(self):
        """Test basic glue functionality using CommentItem and CommentLine
        items.
        """
        diagram = UML.create(UML.Diagram)
        self.main_window.show_diagram(diagram)
        comment = diagram.create(CommentItem, subject=UML.create(UML.Comment))
        assert comment.height == 50
        assert comment.width == 100
        line = diagram.create(CommentLineItem)
        tool = ConnectHandleTool()

        view = self.main_window.get_current_diagram_view()
        assert view, 'View should be available here'

        # select handle:
        handle = line.handles()[-1]
        tool._grabbed_item = line
        tool._grabbed_handle = handle

        # Should glue to (45, 50)
        tool.glue(view, line, handle, 45, 48)

        self.assertEquals((45, 50), view.canvas.get_matrix_i2w(line).transform_point(handle.x, handle.y))

        handle.x, handle.y = 0, 0
        tool.connect(view, line, handle, 45, 48)
        self.assertEquals((45, 50), view.canvas.get_matrix_i2w(line).transform_point(handle.x, handle.y))
        assert handle.connected_to == comment
        assert handle._connect_constraint is not None

