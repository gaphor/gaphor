
import unittest

from gaphor.ui.mainwindow import MainWindow
from gaphor import resource

class MainWindowTestCase(unittest.TestCase):

    def test_creation(self):
        # MainWindow should be created as resource
        main_w = resource(MainWindow)
        main_w.construct()
        self.assertEqual(main_w.get_current_diagram(), None)


# vim:sw=4:et:ai
