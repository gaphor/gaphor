import pytest
from typing import Dict

import gaphas, gaphas.examples
from gaphor.plugins.diagramexport import DiagramExport
import gaphor.ui.menufragment


@pytest.fixture
def diagram_export():
    properties: Dict[str, str] = {}
    export_menu = gaphor.ui.menufragment.MenuFragment()

    return DiagramExport(diagrams=None, properties=properties, export_menu=export_menu)


@pytest.fixture
def canvas():
    c = gaphas.Canvas()
    c.add(gaphas.examples.Box())
    return c


def test_export_to_svg(diagram_export, canvas, tmp_path):
    f = tmp_path / "test.svg"

    diagram_export.save_svg(f, canvas)
    content = f.read_text()

    assert "<svg" in content


def test_export_to_png(diagram_export, canvas, tmp_path):
    f = tmp_path / "test.png"

    diagram_export.save_png(f, canvas)
    content = f.read_bytes()

    assert b"PNG" in content


def test_export_to_pdf(diagram_export, canvas, tmp_path):
    f = tmp_path / "test.pdf"

    diagram_export.save_pdf(f, canvas)
    content = f.read_bytes()

    assert b"%PDF" in content
