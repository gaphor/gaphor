import gaphor.UML as UML
from gaphor.diagram import items
from gaphor.tests.testcase import TestCase

class ObjectNodeTestCase(TestCase):
    def test_object_node(self):
        self.create(items.ObjectNodeItem, UML.ObjectNode)

# vim:sw=4:et:ai

