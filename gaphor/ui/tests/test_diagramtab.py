
import unittest

from gaphor import UML
from gaphor.application import Application
from gaphor.ui.diagramtab import DiagramTab
from gaphor.ui.mainwindow import MainWindow

# ensure actions are loaded:
import gaphor.actions

class DiagramTabTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(services=['element_factory', 'gui_manager', 'action_manager', 'properties'])
        main_window = Application.get_service('gui_manager').main_window
        self.diagram = UML.create(UML.Diagram)
        self.tab = DiagramTab(main_window)
        self.tab.set_diagram(self.diagram)
        self.assertEquals(self.tab.diagram, self.diagram)
        widget = self.tab.construct()
        main_window.add_tab(self.tab, widget, 'title')
        self.assertEquals(self.tab.view.canvas, self.diagram.canvas)
        self.assertEquals(len(UML.lselect()), 1)

    def tearDown(self):
        self.tab.close()
        del self.tab
        self.diagram.unlink()
        del self.diagram
        Application.shutdown()
        assert len(UML.lselect()) == 0

    def test_creation(self):
        pass

    def test_placement(self):
        tab = self.tab
        diagram = self.diagram
        from gaphas import Element
        from gaphas.examples import Box
        box = Box()
        self.assertEquals(len(tab.view._item_bounds), 0)
        diagram.canvas.add(box)
        diagram.canvas.update_now()
        tab.view.request_update([box])
        assert len(tab.view._item_bounds) == 1, tab.view._item_bounds
        assert tab.view._item_bounds.keys()[0] is box, tab.view._item_bounds.keys()[0]
        
        from gaphor.diagram.comment import CommentItem
        comment = self.diagram.create(CommentItem, subject=UML.create(UML.Comment))
        self.assertEquals(len(tab.view._item_bounds), 2)
        self.assertEquals(len(UML.lselect()), 2)
        
