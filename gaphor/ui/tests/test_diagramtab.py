
import unittest

from gaphor import resource, UML
from gaphor.ui.diagramtab import DiagramTab
from gaphor.ui.mainwindow import MainWindow

# ensure actions are loaded:
import gaphor.actions

class DiagramTabTestCase(unittest.TestCase):

    def setUp(self):
        UML.flush()
        self.diagram = UML.create(UML.Diagram)
        self.tab = DiagramTab(self.main_window)
        self.tab.set_diagram(self.diagram)
        self.assertEquals(self.tab.diagram, self.diagram)
        self.tab.construct()
        self.assertEquals(self.tab.view.canvas, self.diagram.canvas)
        self.assertEquals(len(UML.select()), 1)

    def tearDown(self):
        self.tab.close()
        del self.tab
        self.diagram.unlink()
        del self.diagram
        UML.flush()
        assert len(UML.select()) == 0

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
        self.assertEquals(len(tab.view._item_bounds), 1)
        self.assertEquals(tab.view._item_bounds.keys()[0], box)
        #diagram.canvas.add(Element())
        from gaphor.diagram.elementitem import ElementItem
        from gaphor.diagram.comment import CommentItem
        comment = self.diagram.create(CommentItem, subject=UML.create(UML.Comment))
        self.assertEquals(len(tab.view._item_bounds), 2)
        self.assertEquals(len(UML.select()), 2)
        
