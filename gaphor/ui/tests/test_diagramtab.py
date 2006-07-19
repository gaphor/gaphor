
import unittest

from gaphor import resource, UML
from gaphor.ui.diagramtab import DiagramTab
from gaphor.ui.mainwindow import MainWindow

class DiagramTabTestCase(unittest.TestCase):

    main_window = resource(MainWindow)
    main_window.construct()

    def setUp(self):
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
        self.assertEquals(len(tab.view._item_bounds), 1)
        self.assertEquals(tab.view._item_bounds.keys()[0], box)
        #diagram.canvas.add(Element())
        from gaphor.diagram.elementitem import ElementItem
        from gaphor.diagram.comment import CommentItem
        comment = self.diagram.create(CommentItem)
        self.assertEquals(len(tab.view._item_bounds), 2)
        self.assertEquals(len(UML.select()), 2)
        
