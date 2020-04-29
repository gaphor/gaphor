from typing import Dict, List, Set

import pytest

from gaphor.codegen.profile_coder import (
    breadth_first_search,
    create_class_trees,
    create_referenced,
    filter_uml_classes,
    find_root_nodes,
    write_attributes,
)
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML import uml as UML
from gaphor.UML.classes import ClassItem
from gaphor.UML.classes.generalization import GeneralizationItem


class PseudoFile:
    def __init__(self):
        self.data = ""

    def write(self, data):
        self.data += data

    def close(self):
        pass


@pytest.fixture
def filename():
    return PseudoFile()


@pytest.fixture
def class_items(element_factory) -> Dict[int, ClassItem]:
    """Create tree using ClassItems and UML.Generalizations.
    |- 0
    |  |- 1
    |  |- 2
    |  |  |- 3
    |  |  |- 4

    """
    diagram = element_factory.create(UML.Diagram)
    class_items = {
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
        connect(gens[n], gens[n].head, class_items[class_connections[n * 2]])
        connect(gens[n], gens[n].tail, class_items[class_connections[n * 2 + 1]])
    return class_items


@pytest.fixture
def classes(class_items) -> List[UML.Class]:
    return [cls_item.subject for cls_item in class_items.values()]


@pytest.fixture
def tree(classes) -> Dict[UML.Class, List[UML.Class]]:
    """Create tree of UML.Class."""
    tree = create_class_trees(classes)
    assert len(tree) is 5
    return tree


def test_breadth_first_search(tree, classes):
    """Test simple tree structure using BFS."""
    found_classes = breadth_first_search(tree, classes[0])

    assert len(found_classes) is 5
    assert len(found_classes) == len(set(found_classes))


def test_find_root_nodes(tree, classes):
    """Test finding the root nodes."""
    referenced: Set[UML.Class] = set([classes[0], classes[2]])

    root_node = find_root_nodes(tree, referenced)

    assert root_node[0] is classes[0]


def test_write_attributes_no_attribute(filename, element_factory):
    """Test writing pass when no attributes."""
    diagram = element_factory.create(UML.Diagram)
    cls_item = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    write_attributes(cls_item.subject, filename)

    assert filename.data == "    pass\n\n"


def test_type_converter():
    assert True


def test_filter_uml_classes(classes):
    """Test filtering of classes between UML and others."""
    classes[0].name = "~Class"
    classes[1].name = "Class"
    classes[2].name = "Behavior"
    classes[3].name = "Transportation"
    classes[4].name = "Car"
    assert len(classes) is 5

    classes, uml_classes = filter_uml_classes(classes)

    assert len(classes) is 2
    assert len(uml_classes) is 2


def test_create_referenced(classes):
    """Test list of referenced UML.Class objects."""
    referenced = create_referenced(classes)

    assert len(referenced) is 2
    ref_iter = iter(referenced)
    assert next(ref_iter) == classes[0]
    assert next(ref_iter) == classes[2]
