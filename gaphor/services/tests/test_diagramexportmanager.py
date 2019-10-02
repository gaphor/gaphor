import pytest

import gaphas, gaphas.examples
from gaphor.services.diagramexportmanager import DiagramExportManager


@pytest.fixture
def diagram_export_manager():
    properties = {}

    return DiagramExportManager(component_registry=None, properties=properties)


@pytest.fixture
def canvas():
    c = gaphas.Canvas()
    c.add(gaphas.examples.Box())
    return c


def test_export_to_svg(diagram_export_manager, canvas, tmp_path):
    f = tmp_path / "test.svg"

    diagram_export_manager.save_svg(f, canvas)
    content = f.read_text()

    assert "<svg" in content


def test_export_to_png(diagram_export_manager, canvas, tmp_path):
    f = tmp_path / "test.png"

    diagram_export_manager.save_png(f, canvas)
    content = f.read_bytes()

    assert b"PNG" in content


def test_export_to_pdf(diagram_export_manager, canvas, tmp_path):
    f = tmp_path / "test.pdf"

    diagram_export_manager.save_pdf(f, canvas)
    content = f.read_bytes()

    assert b"%PDF" in content
