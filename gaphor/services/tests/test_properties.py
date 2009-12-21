
from unittest import TestCase
from gaphor.services.properties import Properties, FileBackend
import tempfile

class TestProperties(TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        backend = FileBackend(self.tmpdir)
        self.properties = Properties(backend)
        self.properties.init(None)

    def shutDown(self):
        self.properties.shutdown()
        os.remove(os.path.join(self.tmpdir, FileBackend.RESOURCE_FILE))
        os.rmdir(self.tmpdir)

    def test_properties(self):
        prop = self.properties
        prop.set('test1', 2)
        assert 2 == prop('test1')
        assert 3 == prop('test2', 3)
        assert 3 == prop('test2', 4)

# vim:sw=4:et:ai
