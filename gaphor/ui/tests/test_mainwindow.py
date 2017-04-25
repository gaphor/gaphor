
from __future__ import absolute_import
import unittest

from gaphor.application import Application
from gaphor.UML import uml2

class MainWindowTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(services=['element_factory', 'properties', 'main_window', 'ui_manager', 'action_manager'])

    def tearDown(self):
        Application.shutdown()

    def test_creation(self):
        # MainWindow should be created as resource
        main_w = Application.get_service('main_window')
        main_w.open()
        self.assertEqual(main_w.get_current_diagram(), None)

    def test_show_diagram(self):
        main_w = Application.get_service('main_window')
        element_factory = Application.get_service('element_factory')
        diagram = element_factory.create(uml2.Diagram)
        main_w.open()
        self.assertEqual(main_w.get_current_diagram(), None)

        main_w.show_diagram(diagram)
        
# vim:sw=4:et:ai
