import cairo
import pytest
from gaphas.geometry import Rectangle

from gaphor.diagram.shapes import Box, IconBox, Text


@pytest.fixture
def fixed_text_size(monkeypatch):
    size = (60, 15)

    def text_size(*args):
        return size

    monkeypatch.setattr("gaphor.diagram.shapes.text_size", text_size)
    return size


@pytest.fixture
def cr():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
    cr = cairo.Context(surface)
    return cr


def test_box_size():
    box = Box()

    assert box.size(cr=None) == (0, 0)


def test_draw_empty_box():
    box = Box(draw=None)

    box.draw(context=None, bounding_box=Rectangle())


def test_draw_box_with_custom_draw_function():
    called = False

    def draw(box, context, bounding_box):
        nonlocal called
        called = True

    box = Box(draw=draw)

    box.draw(context=None, bounding_box=Rectangle())

    assert called


def test_draw_icon_box(cr):
    box_drawn = None

    def box_draw(box, context, bounding_box):
        nonlocal box_drawn
        box_drawn = bounding_box

    shape = IconBox(Box(draw=box_draw), Text(text="some text"))

    bounding_box = Rectangle(11, 12, 13, 14)
    shape.draw(cr, bounding_box)

    assert box_drawn == bounding_box


def test_text_has_width(cr, fixed_text_size):
    text = Text(lambda: "some text")

    w, _ = text.size(cr)
    assert w == fixed_text_size[0]


def test_text_has_height(cr, fixed_text_size):
    text = Text("some text")

    _, h = text.size(cr)
    assert h == fixed_text_size[1]


def test_text_with_min_width(cr):
    style = {"min-width": 100, "min-height": 0}
    text = Text("some text", style=style)

    w, _ = text.size(cr)
    assert w == 100


def test_text_width_min_height(cr):
    style = {"min-width": 0, "min-height": 40}
    text = Text("some text", style=style)

    _, h = text.size(cr)
    assert h == 40
