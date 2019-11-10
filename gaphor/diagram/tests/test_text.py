import pytest
from gaphas.canvas import instant_cairo_context

from gaphor.diagram.text import (
    FontStyle,
    FontWeight,
    TextAlign,
    TextDecoration,
    VerticalAlign,
    text_point_at_line,
    text_size,
)


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
    x, y = text_point_at_line(points, (10, 5), TextAlign.LEFT)

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
    x, y = text_point_at_line(points, (10, 5), TextAlign.RIGHT)

    assert x == point_at_line[0]
    assert y == point_at_line[1]


@pytest.mark.parametrize(
    "points,point_at_line",
    [
        [[(2.0, 2.0), (22.0, 7.0)], (7, 8.75)],
        [[(2.0, 2.0), (22.0, -3.0)], (7, 3.75)],
        [[(2.0, 2.0), (-18.0, 7.0)], (-13, 8.75)],
        [[(2.0, 2.0), (-18.0, -3.0)], (-13, 3.75)],
        [[(2.0, 2.0), (7.0, 22.0)], (-9.125, 9.5)],
        [[(2.0, 2.0), (7.0, -18.0)], (8.125, -10.5)],
        [[(2.0, 2.0), (-3.0, 22.0)], (3.125, 9.5)],
        [[(2.0, 2.0), (-3.0, -18.0)], (-14.125, -10.5)],
        [[(2.0, 2.0), (22.0, 2.0)], (7, 5.0)],
        [[(2.0, 2.0), (-18.0, 2.0)], (-13, 5.0)],
        [[(2.0, 2.0), (2.0, 22.0)], (5.0, 9.5)],
        [[(2.0, 2.0), (2.0, -18.0)], (5.0, -10.5)],
    ],
)
def test_point_at_center_bottom(points, point_at_line):
    """
    Test aligned at the line text position calculation, horizontal mode
    """
    x, y = text_point_at_line(points, (10, 5), TextAlign.CENTER)

    assert x == pytest.approx(point_at_line[0])
    assert y == pytest.approx(point_at_line[1])


@pytest.fixture
def cr():
    return instant_cairo_context()


def test_text_with_font_as_string(cr):
    w, h = text_size(cr, "Example", "sans 10")
    assert w
    assert h


def test_text_with_font_as_dict(cr):
    w, h = text_size(
        cr,
        "Example",
        {
            "font": "sans 10",
            "font-style": FontStyle.ITALIC,
            "font-weight": FontWeight.BOLD,
            "text-decoration": TextDecoration.UNDERLINE,
        },
    )
    assert w
    assert h


def test_text_with_font_as_dict_with_values_set_to_none(cr):
    w, h = text_size(
        cr,
        "Example",
        {
            "font": "sans bold 10",
            "font-style": None,
            "font-weight": None,
            "text-decoration": TextDecoration.NONE,
        },
    )
    assert w
    assert h


def test_text_with_just_font_as_dict(cr):
    w, h = text_size(cr, "Example", {"font": "sans 10"})
    assert w
    assert h
