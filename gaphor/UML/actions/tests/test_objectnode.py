import locale

from gaphor import UML
from gaphor.UML.actions.objectnode import ObjectNodeItem


def test_object_node(diagram, element_factory):
    node = element_factory.create(UML.ObjectNode)
    item = diagram.create(ObjectNodeItem, subject=node)

    assert item.subject is node


def test_name(create):
    node = create(ObjectNodeItem, UML.ObjectNode)
    name = node.shape.icon.child.children[1]

    node.subject.name = "Blah"

    assert "Blah" == name.child.text()


def test_ordering(create):
    """Test updating of ObjectNodeItem.ordering."""
    node = create(ObjectNodeItem, UML.ObjectNode)
    ordering = node.shape.children[1]

    node.subject.ordering = "unordered"
    node.show_ordering = True

    language = locale.getlocale()[0]
    if language == "en_US":
        assert "{ ordering = unordered }" == ordering.child.text()
