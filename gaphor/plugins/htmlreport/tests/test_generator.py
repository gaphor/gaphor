"""Tests for the HTML report generator."""

import pytest

from gaphor import UML
from gaphor.plugins.htmlreport.generator import (
    build_model_data,
    build_tree,
    extract_element_info,
    generate_report,
)
from gaphor.UML.classes import ClassItem
from gaphor.UML.recipes import apply_stereotype


@pytest.fixture
def model_with_diagram(diagram, element_factory, create):
    c1 = create(ClassItem, UML.Class)
    c1.subject.name = "MyClass"
    c1.matrix.translate(50, 50)

    diagram.name = "Test Diagram"
    diagram.update(diagram.ownedPresentation)

    return diagram, element_factory


def test_index_html_contains_model_data(model_with_diagram, tmp_path):
    diagram, factory = model_with_diagram
    output_dir = tmp_path / "report"
    generate_report(factory, output_dir)

    html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert "MODEL_DATA" in html
    assert "MyClass" in html
    assert "Test Diagram" in html


def test_build_model_data_structure(model_with_diagram):
    diagram, factory = model_with_diagram
    data = build_model_data(factory)

    assert "elements" in data
    assert "diagrams" in data
    assert "tree" in data

    # Check diagram is present
    assert len(data["diagrams"]) >= 1
    diagram_entry = next(iter(data["diagrams"].values()))
    assert diagram_entry["name"] == "Test Diagram"
    assert "svg_content" in diagram_entry

    # Check element is present
    found_class = False
    for el in data["elements"].values():
        if el["name"] == "MyClass":
            found_class = True
            assert el["type"] == "Class"
            assert len(el["diagrams"]) >= 1
    assert found_class


def test_extract_element_info_with_abstract(element_factory):
    cls = element_factory.create(UML.Class)
    cls.name = "AbstractClass"
    cls.isAbstract = True

    info = extract_element_info(cls)
    assert info is not None
    props = {p["name"]: p["value"] for p in info["properties"]}
    assert "isAbstract" in props


def test_extract_element_info_association(diagram, element_factory, create):
    from gaphor.diagram.tests.fixtures import connect
    from gaphor.UML.classes.association import AssociationItem

    c1 = create(ClassItem, UML.Class)
    c1.subject.name = "Src"
    c2 = create(ClassItem, UML.Class)
    c2.subject.name = "Dst"

    assoc = create(AssociationItem)
    connect(assoc, assoc.head, c1)
    connect(assoc, assoc.tail, c2)

    diagram.update(diagram.ownedPresentation)

    info = extract_element_info(assoc.subject)
    assert info is not None
    assert info["type"] == "Association"
    assert len(info["associations"]) == 2
    types = {a["type"] for a in info["associations"]}
    assert "Src" in types
    assert "Dst" in types


def test_extract_element_info_generalization(element_factory):
    parent = element_factory.create(UML.Class)
    parent.name = "Base"
    child = element_factory.create(UML.Class)
    child.name = "Derived"
    gen = element_factory.create(UML.Generalization)
    gen.general = parent
    gen.specific = child

    info = extract_element_info(child)
    assert len(info["generalizations"]) == 1
    assert info["generalizations"][0]["name"] == "Base"
    assert info["generalizations"][0]["type"] == "Class"


def test_extract_element_info_stereotype(element_factory):
    cls = element_factory.create(UML.Class)
    cls.name = "Controller"
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "service"
    apply_stereotype(cls, stereotype)

    info = extract_element_info(cls)
    assert "service" in info["stereotypes"]


def test_extract_element_info_enumeration(element_factory):
    enum = element_factory.create(UML.Enumeration)
    enum.name = "Color"
    for name in ("Red", "Green", "Blue"):
        lit = element_factory.create(UML.EnumerationLiteral)
        lit.name = name
        enum.ownedLiteral = lit

    info = extract_element_info(enum)
    assert info["type"] == "Enumeration"
    assert len(info["literals"]) == 3
    assert "Red" in info["literals"]
    assert "Green" in info["literals"]
    assert "Blue" in info["literals"]


def test_build_tree_nested_packages(element_factory):
    pkg = element_factory.create(UML.Package)
    pkg.name = "MyPackage"
    cls = element_factory.create(UML.Class)
    cls.name = "Inner"
    cls.package = pkg

    tree = build_tree(element_factory)
    pkg_node = next(n for n in tree if n["name"] == "MyPackage")
    assert any(c["name"] == "Inner" for c in pkg_node["children"])
