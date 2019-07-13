import pytest
import cairo

import gaphor.diagram.text
from gaphor.diagram.text import text_point_at_line, TextAlign, VerticalAlign


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
        [[(2.0, 2.0), (22.0, 7.0)], (7, 5.75)],
        [[(2.0, 2.0), (22.0, -3.0)], (7, 0.75)],
        [[(2.0, 2.0), (-18.0, 7.0)], (-13, 5.75)],
        [[(2.0, 2.0), (-18.0, -3.0)], (-13, 0.75)],
        [[(2.0, 2.0), (7.0, 22.0)], (-6.125, 9.5)],
        [[(2.0, 2.0), (7.0, -18.0)], (3.875, -10.5)],
        [[(2.0, 2.0), (-3.0, 22.0)], (-1.125, 9.5)],
        [[(2.0, 2.0), (-3.0, -18.0)], (-11.125, -10.5)],
        [[(2.0, 2.0), (22.0, 2.0)], (7, 2.0)],
        [[(2.0, 2.0), (-18.0, 2.0)], (-13, 2.0)],
        [[(2.0, 2.0), (2.0, 22.0)], (2.0, 9.5)],
        [[(2.0, 2.0), (2.0, -18.0)], (2.0, -10.5)],
    ],
)
def test_point_at_center_bottom(points, point_at_line):
    """
    Test aligned at the line text position calculation, horizontal mode
    """
    x, y = text_point_at_line(points, (10, 5), TextAlign.CENTER)

    assert x == pytest.approx(point_at_line[0])
    assert y == pytest.approx(point_at_line[1])
