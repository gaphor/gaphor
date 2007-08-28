import unittest
import gaphor.UML as UML
from gaphor.diagram import items
from gaphor.application import Application

class ObjectNodeTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(services=['element_factory'])
        self.element_factory = Application.get_service('element_factory')
        self.diagram = self.element_factory.create(UML.Diagram)

    def shutDown(self):
        Application.shutdown()

    def test_object_node(self):
        return self.diagram.create(items.ObjectNodeItem, subject=self.element_factory.create(UML.ObjectNode))

# vim:sw=4:et:ai

