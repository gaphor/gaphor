
from unittest import TestCase
from gaphor.services.properties import Properties, FileBackend
import tempfile

#class MockApplication(object):
#
#    def __init__(self):
#        self.events = []
#
#    def handle(self, event):
#        self.events.append(event)
#

class TestProperties(TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        backend = FileBackend(self.tmpdir)
        self.properties = Properties(backend)
#        self.app = MockApplication()
        self.properties.init(self.app)

    def shutDown(self):
        self.properties.shutdown()
        os.remove(os.path.join(self.tmpdir, FileBackend.RESOURCE_FILE))
        os.rmdir(self.tmpdir)

#    def test_properties(self):
#        prop = self.properties
#        assert not self.app.events
#
#        prop.set('test1', 2)
#        assert len(self.app.events) == 1, self.app.events
#        event = self.app.events[0]
#        assert 'test1' == event.name
#        assert None is event.old_value
#        assert 2 is event.new_value
#        assert 2 == prop('test1')
#
#        prop.set('test1', 2)
#        assert len(self.app.events) == 1
#
#        prop.set('test1', 'foo')
#        assert len(self.app.events) == 2
#        event = self.app.events[1]
#        assert 'test1' == event.name
#        assert 2 is event.old_value
#        assert 'foo' is event.new_value
#        assert 'foo' == prop('test1')
#
#        assert 3 == prop('test2', 3)
#        assert 3 == prop('test2', 4)


# vim:sw=4:et:ai
