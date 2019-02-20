import unittest

from gaphor import UML
from gaphor.application import Application
from gaphor.core import inject
from gaphor.ui.event import Diagram
from gaphor.ui.interfaces import IUIComponent


class MainWindowTestCase(unittest.TestCase):
    def setUp(self):
        Application.init(
            services=[
                "element_factory",
                "properties",
                "main_window",
                "ui_manager",
                "action_manager",
            ]
        )

    component_registry = inject("component_registry")

    def tearDown(self):
        Application.shutdown()

    def test_creation(self):
        # MainWindow should be created as resource
        main_w = Application.get_service("main_window")
        main_w.open()
        self.assertEqual(
            self.component_registry.get_utility(
                IUIComponent, "diagrams"
            ).get_current_diagram(),
            None,
        )

    def test_show_diagram(self):
        main_w = Application.get_service("main_window")
        element_factory = Application.get_service("element_factory")
        diagram = element_factory.create(UML.Diagram)
        main_w.open()
        self.component_registry.handle(Diagram(diagram))
        self.assertEqual(
            self.component_registry.get_utility(
                IUIComponent, "diagrams"
            ).get_current_diagram(),
            diagram,
        )


# vim:sw=4:et:ai
