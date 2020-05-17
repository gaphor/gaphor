from typing import Dict, List, Type

import pytest

from gaphor.application import distribution
from gaphor.codegen.profile_coder import (
    create_class_trees,
    create_referenced,
    filter_uml_classes,
    find_enumerations,
    generate,
    get_class_extensions,
    header,
    type_converter,
    write_attributes,
    write_properties,
)
from gaphor.core.modeling.properties import attribute, derived
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML import uml as UML
from gaphor.UML.classes import ClassItem
from gaphor.UML.classes.generalization import GeneralizationItem
from gaphor.UML.modelfactory import create_extension
from gaphor.UML.modelinglanguage import UMLModelingLanguage


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
    |- 5  |
    |  |- |- 6

    """
    diagram = element_factory.create(UML.Diagram)
    nodes = {
        n: diagram.create(ClassItem, subject=element_factory.create(UML.Class))
        for n in range(6)
    }
    nodes[6] = diagram.create(ClassItem, subject=element_factory.create(UML.Stereotype))
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

    create_extension(nodes[2].subject, nodes[6].subject)
    create_extension(nodes[5].subject, nodes[6].subject)

    assert len(nodes) == 7
    return nodes


@pytest.fixture
def classes(nodes) -> List[UML.Class]:
    return [cls_item.subject for cls_item in nodes.values()]


@pytest.fixture
def tree(classes) -> Dict[UML.Class, List[UML.Class]]:
    """Create tree of UML.Class."""
    tree = create_class_trees(classes)
    assert len(tree) == 7
    return tree


def test_get_class_extension(classes):
    """Test getting meta class using UML.Extension."""
    meta_classes = get_class_extensions(classes[6])
    meta = [cls for cls in meta_classes]
    assert classes[2] in meta


def test_type_converter_boolean(element_factory):
    """Test type convert for boolean."""
    prop = element_factory.create(UML.Property)
    prop.typeValue = "boolean"
    assert type_converter(prop) == "int"


def test_type_converter_int(element_factory):
    """Test type convert for an integer."""
    prop = element_factory.create(UML.Property)
    prop.typeValue = "integer"
    assert type_converter(prop) == "int"


def test_type_converter_str(element_factory):
    """Test type convert for a string."""
    prop = element_factory.create(UML.Property)
    prop.typeValue = "string"
    assert type_converter(prop) == "str"


def test_type_converter_other(element_factory):
    """Test type convert for other type."""
    prop = element_factory.create(UML.Property)
    prop.typeValue = "other_type"
    assert type_converter(prop) == "other_type"


def test_type_converter_none(element_factory):
    """Test type convert with no type."""
    prop = element_factory.create(UML.Property)
    with pytest.raises(ValueError):
        assert type_converter(prop)


def test_write_attributes_no_attribute(filename, element_factory):
    """Test writing pass when no attributes."""
    diagram = element_factory.create(UML.Diagram)
    cls_item = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    write_attributes(cls_item.subject, filename)

    assert filename.data == "    pass\n\n"


def test_write_attributes_for_derived(filename, element_factory):
    """Test writing derived attribute."""
    diagram = element_factory.create(UML.Diagram)
    book = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    book.subject.name = "Book"
    book.subject.title = attribute("title", str)
    book.subject.loanPeriod = attribute("loadPeriod", int, default=14)

    library_book = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    library_book.subject.name = "Library Book"
    library_book.subject.loanPeriod = derived(
        book.subject, "loanPeriod", int, 0, 1, lambda e: [e]
    )
    gen = diagram.create(
        GeneralizationItem, subject=element_factory.create(UML.Generalization)
    )
    connect(gen, gen.tail, library_book)
    connect(gen, gen.head, book)

    write_attributes(library_book.subject, filename)

    assert filename.data == "    pass\n\n"
    # TODO: This should be a derived attribute
    # assert filename.data == "    loanPeriod: derived[int]\n\n"


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
    classes[6].name = "Van"
    assert len(classes) == 7

    uml_classes = filter_uml_classes(classes, UMLModelingLanguage())

    assert len(uml_classes) == 2


def test_find_enumerations(classes):
    """Test filtering of classes between UML and others."""
    classes[0].name = "VehicleTypeKind"
    classes[1].name = "WheelKind"
    classes[2].name = "Behavior"
    classes[3].name = "Transportation"
    classes[4].name = "Car"
    classes[5].name = "Truck"
    classes[6].name = "Van"
    assert len(classes) == 7

    classes, enumerations = find_enumerations(classes)

    assert len(enumerations) == 2
    assert len(classes) == 5


def test_write_properties_enumeration(filename, element_factory):
    """"""
    diagram = element_factory.create(UML.Diagram)
    cls_item = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    enum_item = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    enum_item.subject.name = "VehicleTypeKind"
    enum_item.subject.car = attribute
    enumerations = {enum_item.subject.name: enum_item.subject}

    write_properties(cls_item.subject, filename, enumerations)

    # TODO: complete test for enumeration
    assert filename.data == ""


def test_create_referenced(classes):
    """Test list of referenced UML.Class objects."""
    referenced = create_referenced(classes)
    assert len(referenced) == 3

    nodes = [0, 2, 5]
    for node in nodes:
        assert classes[node] in referenced


def test_model_header(tmp_path):
    """Load a model with no relationships to test header."""
    path = distribution().locate_file("test-models/multiple-messages.gaphor")
    outfile = tmp_path / "profile.py"

    generate(path, outfile)

    assert header in outfile.read_text()


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
