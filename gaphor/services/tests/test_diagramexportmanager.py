
import unittest
from gaphor.application import Application
from gaphor.services.diagramexportservice import DiagramExportService

class DiagramExportServiceTestCase(unittest.TestCase):
    
    def setUp(self):
        Application.init(services=['gui_manager', 'properties', 'element_factory', 'diagram_export', 'action_manager' ])

    def shutDown(self):
        Application.shutdown()

    def test_init(self):
        des = DiagramExportService()
        des.init(None)

    def test_init_from_application(self):
        Application.get_service('diagram_export')
        Application.get_service('gui_manager')


# vim:sw=4:et:ai
