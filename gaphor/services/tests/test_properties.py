
from unittest import TestCase
from gaphor.services.properties import Properties

class TestProperties(TestCase):

    def test_properties(self):
        prop = Properties()
        prop.init(None)
        prop.set('test1', 2)
        assert 2 == prop('test1')
        assert 3 == prop('test2', 3)
        assert 3 == prop('test2', 4)
        prop.shutdown()

