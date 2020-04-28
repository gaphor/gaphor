import pprint
from typing import Dict, List

import pytest

from gaphor.codegen.profile_coder import (
    breadth_first_search,
    filter_uml_classes,
    find_root_nodes,
)
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML import uml as UML
from gaphor.UML.classes import ClassItem
from gaphor.UML.classes.generalization import GeneralizationItem


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
def tree(class_items) -> Dict[UML.Class, List[UML.Class]]:
    """Create tree of UML.Class."""
    tree: Dict[UML.Class, List[UML.Class]] = {}
    for cls in class_items.values():
        tree[cls.subject] = [g for g in cls.subject.general]
    assert len(tree) is 5
    return tree


def test_breadth_first_search(tree, class_items):
    """Test simple tree structure using BFS."""
    found_classes = breadth_first_search(tree, class_items[0].subject)

    assert len(found_classes) is 5
    assert len(found_classes) == len(set(found_classes))


def test_find_root_nodes(tree, class_items):
    """Test finding the root nodes."""
    referenced: List[UML.Class] = []
    referenced.append(class_items[0].subject)
    referenced.append(class_items[2].subject)
    root_node = find_root_nodes(tree, referenced)
    assert root_node[0] is class_items[0].subject


def test_write_attributes():
    assert True


def test_type_converter():
    assert True


def test_filter_uml_classes(class_items):
    """Test filtering of classes between UML and others."""
    classes = [cls.subject for cls in class_items.values()]
    classes[0].name = "~Class"
    classes[1].name = "Class"
    classes[2].name = "Behavior"
    classes[3].name = "Transportation"
    classes[4].name = "Car"
    assert len(classes) is 5

    classes, uml_classes = filter_uml_classes(classes)

    assert len(classes) is 2
    assert len(uml_classes) is 2


def test_create_class_trees():
    assert True


def test_create_referenced():
    assert True
