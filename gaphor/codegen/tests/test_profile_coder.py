from gaphor.codegen.profile_coder import breadth_first_search
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML import uml as UML
from gaphor.UML.classes import ClassItem
from gaphor.UML.classes.generalization import GeneralizationItem


def test_breadth_first_search(element_factory):
    """Test simple tree structure using BFS.
    |- 0
    |  |- 1
    |  |- 2
    |  |  |- 3
    |  |  |- 4
    """
    diagram = element_factory.create(UML.Diagram)
    classes = {
        n: diagram.create(ClassItem, subject=element_factory.create(UML.Class))
        for n in range(5)
    }
    gens = {
        n: diagram.create(
            GeneralizationItem, subject=element_factory.create(UML.Generalization)
        )
        for n in range(4)
    }
    class_connections = [0, 1, 0, 2, 2, 3, 2, 4]
    for n in range(4):
        connect(gens[n], gens[n].head, classes[class_connections[n * 2]])
        connect(gens[n], gens[n].tail, classes[class_connections[n * 2 + 1]])

    tree = {}
    for cls in classes.values():
        tree[cls.subject] = [g for g in cls.subject.general]
    assert len(tree) is 5
    found_classes = breadth_first_search(tree, classes[0].subject)

    assert len(found_classes) is 5
    assert len(found_classes) == len(set(found_classes))


def test_write_attributes():
    assert True


def test_type_converter():
    assert True
