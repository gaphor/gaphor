from __future__ import absolute_import

from gaphor.tests.testcase import TestCase
from gaphor.ui.elementeditor import ElementEditor


class ElementEditorTestCase(TestCase):
    services = TestCase.services + ['main_window', 'ui_manager', 'action_manager', 'properties']

    def test1(self):
        window = ElementEditor()
        assert len(window.action_group.list_actions()) == 1, window.action_group.list_actions()
        window.open()
        window.close()
