
import unittest

class ActionManagerTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testLoadAll(self):
        from gaphor.application import Application
        Application.init()
        am = Application.get_service('action_manager')
        ui = am.ui_manager.get_ui()
        print ui
