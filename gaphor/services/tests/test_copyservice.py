
import unittest
from gaphor.services.copyservice import CopyService
from gaphor.application import Application

class CopyServiceTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(services=['gui_manager', 'action_manager', 'element_factory'])

    def tearDown(self):
        pass

    def test_copy_buffer(self):
        pass


# vim:sw=4:et
