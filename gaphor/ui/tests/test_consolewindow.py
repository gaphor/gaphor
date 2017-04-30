from __future__ import absolute_import

from gaphor.tests.testcase import TestCase
from gaphor.ui.consolewindow import ConsoleWindow


class ConsoleWindowTestCase(TestCase):
    services = TestCase.services + ['main_window', 'ui_manager', 'action_manager', 'properties']

    def test1(self):
        window = ConsoleWindow()
        assert len(window.action_group.list_actions()) == 2, window.action_group.list_actions()
        window.open()
        window.close()
