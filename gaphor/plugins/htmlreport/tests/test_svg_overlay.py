"""Tests for SVG overlay injection."""

import xml.etree.ElementTree as ET

import pytest

from gaphor import UML
from gaphor.diagram.export import save_svg
from gaphor.diagram.general.simpleitem import Box
from gaphor.diagram.tests.fixtures import connect
from gaphor.plugins.htmlreport.svg_overlay import (
    compute_svg_offset,
    inject_overlays,
    item_svg_bounds,
)
from gaphor.UML.classes import ClassItem
from gaphor.UML.classes.association import AssociationItem


@pytest.fixture
def diagram_with_classes(diagram, element_factory, create):
    c1 = create(ClassItem, UML.Class)
    c1.subject.name = "ClassA"
    c2 = create(ClassItem, UML.Class)
    c2.subject.name = "ClassB"

    # Position them apart
    c1.matrix.translate(50, 50)
    c2.matrix.translate(250, 50)
    diagram.update(diagram.ownedPresentation)

    return diagram, c1, c2


def test_compute_svg_offset(diagram_with_classes):
    diagram, c1, c2 = diagram_with_classes
    tx, ty = compute_svg_offset(diagram)
    assert isinstance(tx, float)
    assert isinstance(ty, float)


def test_item_svg_bounds_element(diagram_with_classes):
    diagram, c1, c2 = diagram_with_classes
    tx, ty = compute_svg_offset(diagram)
    bounds = item_svg_bounds(c1, tx, ty)
    assert bounds is not None
    assert bounds.width > 0
    assert bounds.height > 0


def test_item_svg_bounds_no_subject(diagram):
    box = diagram.create(Box)
    diagram.update(diagram.ownedPresentation)
    bounds = item_svg_bounds(box, 0, 0)
    assert bounds is None


def test_inject_overlays_adds_links(diagram_with_classes, tmp_path):
    diagram, c1, c2 = diagram_with_classes
    svg_path = tmp_path / "test.svg"
    save_svg(str(svg_path), diagram)
    inject_overlays(str(svg_path), diagram)

    content = svg_path.read_text(encoding="utf-8")
    assert f"#element/{c1.subject.id}" in content
    assert f"#element/{c2.subject.id}" in content

    # Parse and verify structure
    tree = ET.parse(str(svg_path))
    root = tree.getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}
    links = root.findall(".//svg:a", ns)
    assert len(links) >= 2

    # Check that rects are present inside links
    rects = root.findall(".//svg:a/svg:rect", ns)
    assert len(rects) >= 2


def test_inject_overlays_with_line(diagram, element_factory, create, tmp_path):
    c1 = create(ClassItem, UML.Class)
    c1.subject.name = "Src"
    c1.matrix.translate(50, 50)

    c2 = create(ClassItem, UML.Class)
    c2.subject.name = "Dst"
    c2.matrix.translate(300, 50)

    assoc = create(AssociationItem)
    connect(assoc, assoc.head, c1)
    connect(assoc, assoc.tail, c2)

    diagram.update(diagram.ownedPresentation)

    svg_path = tmp_path / "test_line.svg"
    save_svg(str(svg_path), diagram)
    inject_overlays(str(svg_path), diagram)

    # Lines with subjects should have polyline overlays
    ns = {"svg": "http://www.w3.org/2000/svg"}
    tree = ET.parse(str(svg_path))
    root = tree.getroot()
    links = root.findall(".//svg:a", ns)
    # At least 2 class rects + potentially the association line
    assert len(links) >= 2
