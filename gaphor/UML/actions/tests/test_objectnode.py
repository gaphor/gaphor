from gaphor import UML
from gaphor.UML.actions.objectnode import ObjectNodeItem


def test_object_node(diagram, element_factory):
    node = element_factory.create(UML.ObjectNode)
    item = diagram.create(ObjectNodeItem, subject=node)

    assert item.subject is node


def test_name(diagram, element_factory):
    """Test updating of object node name."""
    node = diagram.create(
        ObjectNodeItem, subject=element_factory.create(UML.ObjectNode)
    )
    name = node.shape.icon.children[1]

    node.subject.name = "Blah"

    assert "Blah" == name.text()


def test_ordering(diagram, element_factory):
    """Test updating of ObjectNodeItem.ordering."""
    node = diagram.create(
        ObjectNodeItem, subject=element_factory.create(UML.ObjectNode)
    )
    ordering = node.shape.children[1]

    node.subject.ordering = "unordered"
    node.show_ordering = True

    assert "{ ordering = unordered }" == ordering.text()
