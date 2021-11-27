import pytest

from gaphor.diagram.export import save_pdf, save_png, save_svg
from gaphor.diagram.general import Box


@pytest.fixture
def diagram_with_box(diagram):
    diagram.create(Box)
    return diagram


def test_export_to_svg(diagram_with_box, tmp_path):
    f = tmp_path / "test.svg"

    save_svg(f, diagram_with_box)
    content = f.read_text()

    assert "<svg" in content


def test_export_to_png(diagram_with_box, tmp_path):
    f = tmp_path / "test.png"

    save_png(f, diagram_with_box)
    content = f.read_bytes()

    assert b"PNG" in content


def test_export_to_pdf(diagram_with_box, tmp_path):
    f = tmp_path / "test.pdf"

    save_pdf(f, diagram_with_box)
    content = f.read_bytes()

    assert b"%PDF" in content
