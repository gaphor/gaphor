import unittest

from gaphas.examples import Box

from gaphor import UML
from gaphor.application import Application
from gaphor.diagram.general.comment import CommentItem
from gaphor.ui.mainwindow import DiagramPage


class DiagramPageTestCase(unittest.TestCase):
    def setUp(self):
        Application.init(
            services=[
                "event_manager",
                "component_registry",
                "element_factory",
                "main_window",
                "action_manager",
                "properties",
                "namespace",
                "diagrams",
                "toolbox",
            ]
        )
        main_window = Application.get_service("main_window")
        main_window.open()
        self.element_factory = Application.get_service("element_factory")
        self.diagram = self.element_factory.create(UML.Diagram)
        self.page = DiagramPage(
            self.diagram,
            Application.get_service("event_manager"),
            self.element_factory,
            Application.get_service("properties"),
        )
        self.page.construct()
        assert self.page.diagram == self.diagram
        assert self.page.view.canvas == self.diagram.canvas
        assert len(self.element_factory.lselect()) == 1

    def tearDown(self):
        self.page.close()
        del self.page
        self.diagram.unlink()
        del self.diagram
        Application.shutdown()
        assert len(self.element_factory.lselect()) == 0

    def test_creation(self):
        pass

    def test_placement(self):
        box = Box()
        self.diagram.canvas.add(box)
        self.diagram.canvas.update_now()
        self.page.view.request_update([box])

        comment = self.diagram.create(
            CommentItem, subject=self.element_factory.create(UML.Comment)
        )
        assert len(self.element_factory.lselect()) == 2
