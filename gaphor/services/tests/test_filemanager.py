
import unittest
from gaphor.application import Application
from gaphor.services.filemanager import FileManager


class FileManagerTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(services=['file_manager', 'element_factory', 'properties', 'gui_manager'])

    def tearDown(self):
        Application.shutdown()

    def test_recent_files(self):
        fileman = Application.get_service('file_manager')

        # ensure the recent_files list is empty:
        fileman._recent_files = []
        fileman.update_recent_files()
        for i in range(0, 9):
            a = fileman.action_group.get_action('file-recent-%d' % i)
            assert a
            assert a.get_property('visible') == False

        fileman.filename = 'firstfile'
        a = fileman.action_group.get_action('file-recent-%d' % 0)
        assert a
        assert a.get_property('visible') == True
        assert a.props.label == '_1. firstfile', a.props.label
        for i in range(1, 9):
            a = fileman.action_group.get_action('file-recent-%d' % i)
            assert a
            assert a.get_property('visible') == False

