import pytest
import cairo

import gaphor.diagram.text
from gaphor.diagram.text import Text

TEXT_SIZE = (60, 15)


@pytest.fixture(autouse=True)
def mock_pango_cairo(monkeypatch):
    def text_size(*args):
        return TEXT_SIZE

    monkeypatch.setattr("gaphor.diagram.text.text_size", text_size)


@pytest.fixture
def cr():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
    cr = cairo.Context(surface)
    return cr


def test_text_has_width(cr):
    text = Text("some text")

    w, _ = text.size(cr)
    assert w == TEXT_SIZE[0]


def test_text_has_height(cr):
    text = Text("some text")

    _, h = text.size(cr)
    assert h == TEXT_SIZE[1]


def test_text_with_min_width(cr):
    style = {"min-width": 100, "min-height": 0}
    text = Text("some text", style)

    w, _ = text.size(cr)
    assert w == 100


def test_text_width_min_height(cr):
    style = {"min-width": 0, "min-height": 40}
    text = Text("some text", style)

    _, h = text.size(cr)
    assert h == 40
