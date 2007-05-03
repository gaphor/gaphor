
from gaphor.ui.consolewindow import ConsoleWindow
import unittest

class ConsoleWindowTestCase(unittest.TestCase):

    def test1(self):
        window = ConsoleWindow()
        assert len(window.action_group.list_actions()) == 2
        window.construct()
        window.close()

