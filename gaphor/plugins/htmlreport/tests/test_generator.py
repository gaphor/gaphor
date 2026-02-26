"""Tests for the HTML report generator."""

import json

import pytest

from gaphor import UML
from gaphor.plugins.htmlreport.generator import (
    build_model_data,
    build_tree,
    extract_element_info,
    generate_report,
)
from gaphor.UML.classes import ClassItem


@pytest.fixture
def model_with_diagram(diagram, element_factory, create):
    c1 = create(ClassItem, UML.Class)
    c1.subject.name = "MyClass"
    c1.matrix.translate(50, 50)

    diagram.name = "Test Diagram"
    diagram.update(diagram.ownedPresentation)

    return diagram, element_factory


def test_generate_report_creates_files(model_with_diagram, tmp_path):
    diagram, factory = model_with_diagram
    output_dir = tmp_path / "report"
    generate_report(factory, output_dir)

    assert (output_dir / "index.html").exists()
    assert (output_dir / "assets" / "style.css").exists()
    assert (output_dir / "assets" / "report.js").exists()

    # Check that SVG files exist in diagrams/
    svg_files = list((output_dir / "diagrams").glob("*.svg"))
    assert len(svg_files) >= 1


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
    assert "svg_file" in diagram_entry

    # Check element is present
    found_class = False
    for el in data["elements"].values():
        if el["name"] == "MyClass":
            found_class = True
            assert el["type"] == "Class"
            assert len(el["diagrams"]) >= 1
    assert found_class


def test_build_tree(model_with_diagram):
    _, factory = model_with_diagram
    tree = build_tree(factory)
    assert isinstance(tree, list)
    assert len(tree) > 0

    # Find diagram in tree
    names = [n["name"] for n in tree]
    # The tree should contain the diagram or its elements
    assert any("Test Diagram" in n or "MyClass" in n for n in names)


def test_extract_element_info(element_factory):
    cls = element_factory.create(UML.Class)
    cls.name = "ExtractTest"

    info = extract_element_info(cls)
    assert info is not None
    assert info["name"] == "ExtractTest"
    assert info["type"] == "Class"


def test_extract_element_info_with_abstract(element_factory):
    cls = element_factory.create(UML.Class)
    cls.name = "AbstractClass"
    cls.isAbstract = True

    info = extract_element_info(cls)
    assert info is not None
    props = {p["name"]: p["value"] for p in info["properties"]}
    assert "isAbstract" in props


def test_model_data_json_serializable(model_with_diagram):
    _, factory = model_with_diagram
    data = build_model_data(factory)
    # Should not raise
    json_str = json.dumps(data)
    assert len(json_str) > 0
