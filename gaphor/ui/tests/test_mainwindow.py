
import gtk
import unittest

from gaphor.application import restart, Application
from gaphor.ui.mainwindow import MainWindow
from gaphor import UML

class MainWindowTestCase(unittest.TestCase):

    def setUp(self):
        restart()
        Application.init(services=['element_factory', 'properties', 'action_manager'])

    def test_creation(self):
        # MainWindow should be created as resource
        main_w = MainWindow()
        ui_manager = gtk.UIManager()
        main_w.ui_manager = ui_manager
        main_w.construct()
        self.assertEqual(main_w.get_current_diagram(), None)


    def test_show_diagram(self):
        main_w = MainWindow()
        element_factory = Application.get_service('element_factory')
        diagram = element_factory.create(UML.Diagram)
        ui_manager = gtk.UIManager()
        main_w.ui_manager = ui_manager
        main_w.construct()
        self.assertEqual(main_w.get_current_diagram(), None)

        main_w.show_diagram(diagram)
        
# vim:sw=4:et:ai
