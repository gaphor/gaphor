
from gaphor.ui.elementeditor import ElementEditor
from gaphor.tests.testcase import TestCase

class ElementEditorTestCase(TestCase):

    services = TestCase.services + ['main_window', 'action_manager', 'properties']

    def test1(self):
        import gtk
        ui_manager = gtk.UIManager()
        window = ElementEditor()
        window.ui_manager = ui_manager
        assert len(window.action_group.list_actions()) == 1, window.action_group.list_actions()
        window.construct()
        window.close()

