
from gaphor.ui.consolewindow import ConsoleWindow
import unittest

class ConsoleWindowTestCase(unittest.TestCase):

    def test1(self):
        import gtk
        ui_manager = gtk.UIManager()
        window = ConsoleWindow()
        window.ui_manager = ui_manager
        assert len(window.action_group.list_actions()) == 3
        window.construct()
        window.close()

