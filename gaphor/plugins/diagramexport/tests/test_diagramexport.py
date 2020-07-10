from typing import Dict

import pytest

import gaphor.ui.menufragment
from gaphor.diagram.general import Box
from gaphor.plugins.diagramexport import DiagramExport


@pytest.fixture
def diagram_export():
    properties: Dict[str, str] = {}
    export_menu = gaphor.ui.menufragment.MenuFragment()

    return DiagramExport(diagrams=None, properties=properties, export_menu=export_menu)


@pytest.fixture
def diagram_with_box(diagram):
    diagram.create(Box)
    return diagram


def test_export_to_svg(diagram_export, diagram_with_box, tmp_path):
    f = tmp_path / "test.svg"

    diagram_export.save_svg(f, diagram_with_box)
    content = f.read_text()

    assert "<svg" in content


def test_export_to_png(diagram_export, diagram_with_box, tmp_path):
    f = tmp_path / "test.png"

    diagram_export.save_png(f, diagram_with_box)
    content = f.read_bytes()

    assert b"PNG" in content


def test_export_to_pdf(diagram_export, diagram_with_box, tmp_path):
    f = tmp_path / "test.pdf"

    diagram_export.save_pdf(f, diagram_with_box)
    content = f.read_bytes()

    assert b"%PDF" in content
