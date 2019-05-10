import gaphor.UML as UML
from gaphor.tests.testcase import TestCase
from ..objectnode import ObjectNodeItem


class ObjectNodeTestCase(TestCase):
    def test_object_node(self):
        self.create(ObjectNodeItem, UML.ObjectNode)

    def test_name(self):
        """
        Test updating of object node name
        """
        node = self.create(ObjectNodeItem, UML.ObjectNode)
        node.subject.name = "Blah"

        self.assertEqual("Blah", node._name.text)

        node.subject = None
        # Undefined

    def test_upper_bound(self):
        """
        TODO: Test upper bound
        """
        pass

    def test_ordering(self):
        """
        Test updating of ObjectNodeItem.ordering.
        """
        node = self.create(ObjectNodeItem, UML.ObjectNode)
        node.subject.ordering = "unordered"

        self.assertEqual("{ ordering = unordered }", node._ordering.text)

        node.show_ordering = True

        self.assertEqual("{ ordering = unordered }", node._ordering.text)

    def test_persistence(self):
        """
        TODO: Test connector item saving/loading
        """
        pass
