import unittest
from gaphor.application import Application
from gaphor.services.diagramexportmanager import DiagramExportManager


class DiagramExportManagerTestCase(unittest.TestCase):
    def setUp(self):
        Application.init(services=["properties", "diagram_export_manager"])

    def shutDown(self):
        Application.shutdown()

    def test_init_from_application(self):
        Application.get_service("diagram_export_manager")
