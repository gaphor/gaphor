import gaphor.UML as UML
from gaphor.diagram.actions.objectnode import ObjectNodeItem
from gaphor.tests.testcase import TestCase


class ObjectNodeTestCase(TestCase):
    def test_object_node(self):
        self.create(ObjectNodeItem, UML.ObjectNode)

    def test_name(self):
        """
        Test updating of object node name
        """
        node = self.create(ObjectNodeItem, UML.ObjectNode)
        name = node.shape.icon.children[1]

        node.subject.name = "Blah"

        assert "Blah" == name.text()

    def test_ordering(self):
        """
        Test updating of ObjectNodeItem.ordering.
        """
        node = self.create(ObjectNodeItem, UML.ObjectNode)
        ordering = node.shape.children[1]

        node.subject.ordering = "unordered"
        node.show_ordering = True

        assert "{ ordering = unordered }" == ordering.text()
