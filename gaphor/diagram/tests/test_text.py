import pytest
import cairo

import gaphor.diagram.text
from gaphor.diagram.text import Text
from gaphor.diagram.style import Style

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


@pytest.fixture
def style():
    return Style(font="sans 10")


def test_text_has_width(cr, style):
    text = Text("some text", style)

    w, _ = text.size(cr)
    assert w == TEXT_SIZE[0]


def test_text_has_height(cr, style):
    text = Text("some text", style)

    _, h = text.size(cr)
    assert h == TEXT_SIZE[1]


def test_text_with_min_width(cr, style):
    style.min_size = (100, 0)
    text = Text("some text", style)

    w, _ = text.size(cr)
    assert w == 100


def test_text_width_min_height(cr, style):
    style.min_size = (0, 40)
    text = Text("some text", style)

    _, h = text.size(cr)
    assert h == 40
