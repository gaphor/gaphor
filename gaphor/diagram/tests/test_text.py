import pytest
import cairo

import gaphor.diagram.text
from gaphor.diagram.text import Text, text_point_at_line, TextAlign, VerticalAlign

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


@pytest.mark.parametrize(
    "points,point_at_line",
    [
        [[(0, 0), (20, 20)], (5, -10)],
        [[(0, 0), (-20, 20)], (-15, -10)],
        [[(0, 0), (20, -20)], (5, 5)],
        [[(0, 0), (-20, -20)], (-15, 5)],
    ],
)
def test_point_at_left_top(points, point_at_line):
    x, y = text_point_at_line(
        points, (10, 5), TextAlign.LEFT, VerticalAlign.TOP, (2, 2, 2, 2)
    )

    assert x == point_at_line[0]
    assert y == point_at_line[1]


@pytest.mark.parametrize(
    "points,point_at_line",
    [
        [[(0, 0), (20, 20)], (5, 25)],
        [[(0, 0), (-20, 20)], (-15, 25)],
        [[(0, 0), (20, -20)], (5, -30)],
        [[(0, 0), (-20, -20)], (-15, -30)],
    ],
)
def test_point_at_right_top(points, point_at_line):
    x, y = text_point_at_line(
        points, (10, 5), TextAlign.RIGHT, VerticalAlign.TOP, (2, 2, 2, 2)
    )

    assert x == point_at_line[0]
    assert y == point_at_line[1]


@pytest.mark.parametrize(
    "points,point_at_line",
    [
        [[(2.0, 2.0), (22.0, 7.0)], (7, -4.75)],
        [[(2.0, 2.0), (22.0, -3.0)], (7, -9.75)],
        [[(2.0, 2.0), (-18.0, 7.0)], (-13, -4.75)],
        [[(2.0, 2.0), (-18.0, -3.0)], (-13, -9.75)],
        [[(2.0, 2.0), (7.0, 22.0)], (7.125, 9.5)],
        [[(2.0, 2.0), (7.0, -18.0)], (-8.125, -10.5)],
        [[(2.0, 2.0), (-3.0, 22.0)], (-13.125, 9.5)],
        [[(2.0, 2.0), (-3.0, -18.0)], (2.125, -10.5)],
        [[(2.0, 2.0), (22.0, 2.0)], (7, -6)],
        [[(2.0, 2.0), (-18.0, 2.0)], (-13, -6)],
        [[(2.0, 2.0), (2.0, 22.0)], (-10, 9.5)],
        [[(2.0, 2.0), (2.0, -18.0)], (-10, -10.5)],
    ],
)
def test_point_at_center_top(points, point_at_line):
    """
    Test aligned at the line text position calculation, horizontal mode
    """
    x, y = text_point_at_line(
        points, (10, 5), TextAlign.CENTER, VerticalAlign.TOP, (3, 2, 3, 2)
    )

    assert x == pytest.approx(point_at_line[0])
    assert y == pytest.approx(point_at_line[1])


@pytest.mark.parametrize(
    "points,point_at_line",
    [
        [[(2.0, 2.0), (22.0, 7.0)], (7, 8.75)],
        [[(2.0, 2.0), (22.0, -3.0)], (7, 3.75)],
        [[(2.0, 2.0), (-18.0, 7.0)], (-13, 8.75)],
        [[(2.0, 2.0), (-18.0, -3.0)], (-13, 3.75)],
        [[(2.0, 2.0), (7.0, 22.0)], (-8.125, 9.5)],
        [[(2.0, 2.0), (7.0, -18.0)], (7.125, -10.5)],
        [[(2.0, 2.0), (-3.0, 22.0)], (2.125, 9.5)],
        [[(2.0, 2.0), (-3.0, -18.0)], (-13.125, -10.5)],
        [[(2.0, 2.0), (22.0, 2.0)], (7, 5)],
        [[(2.0, 2.0), (-18.0, 2.0)], (-13, 5)],
        [[(2.0, 2.0), (2.0, 22.0)], (4, 9.5)],
        [[(2.0, 2.0), (2.0, -18.0)], (4, -10.5)],
    ],
)
def test_point_at_center_bottom(points, point_at_line):
    """
    Test aligned at the line text position calculation, horizontal mode
    """
    x, y = text_point_at_line(
        points, (10, 5), TextAlign.CENTER, VerticalAlign.BOTTOM, (3, 2, 3, 2)
    )

    assert x == pytest.approx(point_at_line[0])
    assert y == pytest.approx(point_at_line[1])
