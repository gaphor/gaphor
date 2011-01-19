
import unittest

from gaphor import UML
from gaphor.application import Application
from gaphor.ui.diagramtab import DiagramTab
from gaphor.ui.mainwindow import MainWindow


class DiagramTabTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(services=['element_factory', 'main_window', 'action_manager', 'properties', 'element_dispatcher'])
        main_window = Application.get_service('main_window')
        element_factory = Application.get_service('element_factory')
        self.element_factory = element_factory
        self.diagram = element_factory.create(UML.Diagram)
        self.tab = DiagramTab(main_window)
        self.tab.set_diagram(self.diagram)
        self.assertEquals(self.tab.diagram, self.diagram)
        widget = self.tab.construct()
        main_window.add_tab(self.tab, widget, 'title')
        self.assertEquals(self.tab.view.canvas, self.diagram.canvas)
        self.assertEquals(len(element_factory.lselect()), 1)

    def tearDown(self):
        self.tab.close()
        del self.tab
        self.diagram.unlink()
        del self.diagram
        Application.shutdown()
        #assert len(self.element_factory.lselect()) == 0

    def test_creation(self):
        pass

    def test_placement(self):
        tab = self.tab
        diagram = self.diagram
        from gaphas import Element
        from gaphas.examples import Box
        box = Box()
        diagram.canvas.add(box)
        diagram.canvas.update_now()
        tab.view.request_update([box])
        
        from gaphor.diagram.comment import CommentItem
        comment = self.diagram.create(CommentItem, subject=self.element_factory.create(UML.Comment))
        self.assertEquals(len(self.element_factory.lselect()), 2)
        
