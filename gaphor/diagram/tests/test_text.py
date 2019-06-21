import pytest
import cairo

from gaphor.diagram.text import Text
from gaphor.diagram.style import Style


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

    text.update_extents(cr)
    assert text.width == 58


def test_text_has_height(cr, style):
    text = Text("some text", style)

    text.update_extents(cr)
    assert text.height == 14


def test_text_with_min_width(cr, style):
    style.min_size = (100, 0)
    text = Text("some text", style)

    text.update_extents(cr)
    assert text.width == 100


def test_text_width_min_height(cr, style):
    style.min_size = (0, 40)
    text = Text("some text", style)

    text.update_extents(cr)
    assert text.height == 40
