
from gaphor.ui.consolewindow import ConsoleWindow
from gaphor.tests.testcase import TestCase

class ConsoleWindowTestCase(TestCase):

    services = TestCase.services + ['main_window', 'action_manager', 'properties']

    def test1(self):
        import gtk
        ui_manager = gtk.UIManager()
        window = ConsoleWindow()
        window.ui_manager = ui_manager
        assert len(window.action_group.list_actions()) == 2, window.action_group.list_actions()
        window.construct()
        window.close()

