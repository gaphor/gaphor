import unittest

from gaphor import UML
from gaphor.application import Application
from gaphor.ui.event import DiagramShow
from gaphor.ui.abc import UIComponent


class MainWindowTestCase(unittest.TestCase):
    def setUp(self):
        Application.init(
            services=[
                "event_manager",
                "component_registry",
                "element_factory",
                "properties",
                "main_window",
                "action_manager",
                "namespace",
                "diagrams",
                "toolbox",
            ]
        )

        self.component_registry = Application.get_service("component_registry")
        self.event_manager = Application.get_service("event_manager")

    def tearDown(self):
        Application.shutdown()

    def get_current_diagram(self):
        return self.component_registry.get(
            UIComponent, "diagrams"
        ).get_current_diagram()

    def test_creation(self):
        # MainWindow should be created as resource
        main_w = Application.get_service("main_window")
        main_w.open()
        assert self.get_current_diagram() is None

    def test_show_diagram(self):
        main_w = Application.get_service("main_window")
        element_factory = Application.get_service("element_factory")
        diagram = element_factory.create(UML.Diagram)
        main_w.open()
        self.event_manager.handle(DiagramShow(diagram))
        assert self.get_current_diagram() == diagram
