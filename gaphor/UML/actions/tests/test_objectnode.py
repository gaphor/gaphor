from gaphor import UML
from gaphor.UML.actions.objectnode import ObjectNodeItem


class TestObjectNode:
    def test_object_node(self, case):
        case.create(ObjectNodeItem, UML.ObjectNode)

    def test_name(self, case):
        """Test updating of object node name."""
        node = case.create(ObjectNodeItem, UML.ObjectNode)
        name = node.shape.icon.children[1]

        node.subject.name = "Blah"

        assert "Blah" == name.text()

    def test_ordering(self, case):
        """Test updating of ObjectNodeItem.ordering."""
        node = case.create(ObjectNodeItem, UML.ObjectNode)
        ordering = node.shape.children[1]

        node.subject.ordering = "unordered"
        node.show_ordering = True

        assert "{ ordering = unordered }" == ordering.text()
