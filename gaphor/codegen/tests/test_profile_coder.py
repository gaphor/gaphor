from typing import Dict, List, Set

import pytest

from gaphor.application import Session, distribution
from gaphor.codegen.profile_coder import (
    breadth_first_search,
    create_class_trees,
    create_referenced,
    filter_uml_classes,
    find_root_nodes,
    generate,
    get_class_extensions,
    header,
    write_attributes,
)
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML import uml as UML
from gaphor.UML.classes import ClassItem
from gaphor.UML.classes.generalization import GeneralizationItem
from gaphor.UML.modelfactory import create_extension


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
def nodes(element_factory) -> Dict[int, ClassItem]:
    """Create tree using ClassItems and Stereotypes.

    All connections use UML.Generalizations, except for node 2 is connected to
    node 5 with an UML.Extension. Node 5 is the only Stereotype, the others are
    Classes.

    |- 0
    |  |- 1
    |  |- 2
    |  |  |- 3
    |  |  |- 4
    |  |  |- 5

    """
    diagram = element_factory.create(UML.Diagram)
    nodes = {
        n: diagram.create(ClassItem, subject=element_factory.create(UML.Class))
        for n in range(5)
    }
    nodes[5] = diagram.create(ClassItem, subject=element_factory.create(UML.Stereotype))
    gens = {
        n: diagram.create(
            GeneralizationItem, subject=element_factory.create(UML.Generalization)
        )
        for n in range(4)
    }
    class_connections = [0, 1, 0, 2, 2, 3, 2, 4]
    for n in range(4):
        connect(gens[n], gens[n].head, nodes[class_connections[n * 2]])
        connect(gens[n], gens[n].tail, nodes[class_connections[n * 2 + 1]])

    create_extension(nodes[2].subject, nodes[5].subject)

    assert len(nodes) == 6
    return nodes


@pytest.fixture
def classes(nodes) -> List[UML.Class]:
    return [cls_item.subject for cls_item in nodes.values()]


@pytest.fixture
def tree(classes) -> Dict[UML.Class, List[UML.Class]]:
    """Create tree of UML.Class."""
    tree = create_class_trees(classes)
    assert len(tree) == 6
    return tree


def test_get_class_extension(classes):
    """Test getting meta class using UML.Extension."""
    meta_classes = get_class_extensions(classes[5])
    meta = [cls for cls in meta_classes]
    assert classes[2] in meta


def test_breadth_first_search(tree, classes):
    """Test simple tree structure using BFS."""
    found_classes = breadth_first_search(tree, classes[0])

    assert len(found_classes) == 6
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
    classes[5].name = "Truck"
    assert len(classes) == 6

    uml_classes = filter_uml_classes(classes)

    assert len(uml_classes) == 2


def test_create_referenced(classes):
    """Test list of referenced UML.Class objects."""
    referenced = create_referenced(classes)

    assert len(referenced) == 2
    ref_iter = iter(referenced)
    assert next(ref_iter) == classes[0] or classes[2]
    assert next(ref_iter) == classes[2] or classes[0]


def test_model_header(tmp_path):
    """Load a model with no relationships to test header."""
    path = distribution().locate_file("test-models/multiple-messages.gaphor")
    outfile = tmp_path / "profile.py"

    generate(path, outfile)

    assert outfile.read_text() == header


def test_model_with_extension(tmp_path):
    """Load a model with an extension relationship."""
    path = distribution().locate_file("test-models/codegen-extension.gaphor")
    outfile = tmp_path / "profile.py"

    generate(path, outfile)

    extension = """
from gaphor.UML import Class

class NewStereotype(Class):
    pass
"""
    assert extension in outfile.read_text()
