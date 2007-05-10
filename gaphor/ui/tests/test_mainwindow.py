
import gtk
import unittest

from gaphor.ui.mainwindow import MainWindow


class MainWindowTestCase(unittest.TestCase):

    def setUp(self):
        from gaphor.application import restart, Application
        restart()
        Application.init(services=['element_factory', 'properties', 'action_manager'])

    def test_creation(self):
        # MainWindow should be created as resource
        main_w = MainWindow()
        ui_manager = gtk.UIManager()
        main_w.ui_manager = ui_manager
        main_w.construct()
        self.assertEqual(main_w.get_current_diagram(), None)


# vim:sw=4:et:ai
