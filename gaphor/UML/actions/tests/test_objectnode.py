from gaphor import UML
from gaphor.UML.actions.objectnode import ObjectNodeItem


def test_object_node(create):
    create(ObjectNodeItem, UML.ObjectNode)


def test_name(create):
    """Test updating of object node name."""
    node = create(ObjectNodeItem, UML.ObjectNode)
    name = node.shape.icon.children[1]

    node.subject.name = "Blah"

    assert "Blah" == name.text()


def test_ordering(create):
    """Test updating of ObjectNodeItem.ordering."""
    node = create(ObjectNodeItem, UML.ObjectNode)
    ordering = node.shape.children[1]

    node.subject.ordering = "unordered"
    node.show_ordering = True

    assert "{ ordering = unordered }" == ordering.text()
