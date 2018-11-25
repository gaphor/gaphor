import unittest

from gaphor import UML
from gaphor.application import Application
from gaphor.ui.diagramtab import DiagramTab
from gaphor.ui.mainwindow import MainWindow


class DiagramTabTestCase(unittest.TestCase):
    def setUp(self):
        Application.init(
            services=[
                "element_factory",
                "main_window",
                "ui_manager",
                "action_manager",
                "properties",
                "element_dispatcher",
            ]
        )
        main_window = Application.get_service("main_window")
        main_window.open()
        element_factory = Application.get_service("element_factory")
        self.element_factory = element_factory
        self.diagram = element_factory.create(UML.Diagram)
        self.tab = main_window.show_diagram(self.diagram)
        self.assertEqual(self.tab.diagram, self.diagram)
        self.assertEqual(self.tab.view.canvas, self.diagram.canvas)
        self.assertEqual(len(element_factory.lselect()), 1)

    def tearDown(self):
        self.tab.close()
        del self.tab
        self.diagram.unlink()
        del self.diagram
        Application.shutdown()
        # assert len(self.element_factory.lselect()) == 0

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

        comment = self.diagram.create(
            CommentItem, subject=self.element_factory.create(UML.Comment)
        )
        self.assertEqual(len(self.element_factory.lselect()), 2)


# vim:sw=4:et:ai
