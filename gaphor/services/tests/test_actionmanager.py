import unittest


class ActionManagerTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testLoadAll(self):
        from gaphor.application import Application

        Application.init()
        am = Application.get_service("action_manager")
        ui = am.ui_manager.get_ui()

        assert '<menuitem name="file-quit" action="file-quit"/>' in ui, ui
        # From filemanager:
        assert '<menuitem name="file-new" action="file-new"/>' in ui, ui
        # From Undomanager
        assert '<toolitem name="edit-undo" action="edit-undo"/>' in ui, ui
