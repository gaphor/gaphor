"""Test item styles."""

import pytest

from gaphor.diagram.style import (
    get_text_point,
    get_min_size,
    ALIGN_LEFT,
    ALIGN_CENTER,
    ALIGN_RIGHT,
    ALIGN_TOP,
    ALIGN_MIDDLE,
    ALIGN_BOTTOM,
)
from gaphor.diagram.text import TextAlign, VerticalAlign


def test_min_size():
    """Test minimum size calculation."""
    width, height = get_min_size(10, 10, (1, 2, 3, 4))
    assert width == 16
    assert height == 14


def test_align_box():
    """Test aligned text position calculation."""
    extents = 80, 12
    padding = (1, 2, 3, 4)
    data = {
        (ALIGN_LEFT, ALIGN_TOP, False): (4, 1),
        (ALIGN_LEFT, ALIGN_MIDDLE, False): (4, 14),
        (ALIGN_LEFT, ALIGN_BOTTOM, False): (4, 25),
        (ALIGN_CENTER, ALIGN_TOP, False): (42, 1),
        (ALIGN_CENTER, ALIGN_MIDDLE, False): (42, 14),
        (ALIGN_CENTER, ALIGN_BOTTOM, False): (42, 25),
        (ALIGN_RIGHT, ALIGN_TOP, False): (78, 1),
        (ALIGN_RIGHT, ALIGN_MIDDLE, False): (78, 14),
        (ALIGN_RIGHT, ALIGN_BOTTOM, False): (78, 25),
        (ALIGN_LEFT, ALIGN_TOP, True): (-84, -13),
        (ALIGN_LEFT, ALIGN_MIDDLE, True): (-84, 14),
        (ALIGN_LEFT, ALIGN_BOTTOM, True): (-84, 43),
        (ALIGN_CENTER, ALIGN_TOP, True): (40, -13),
        (ALIGN_CENTER, ALIGN_MIDDLE, True): (40, 14),
        (ALIGN_CENTER, ALIGN_BOTTOM, True): (40, 43),
        (ALIGN_RIGHT, ALIGN_TOP, True): (162, -13),
        (ALIGN_RIGHT, ALIGN_MIDDLE, True): (162, 14),
        (ALIGN_RIGHT, ALIGN_BOTTOM, True): (162, 43),
    }

    for halign in (TextAlign.LEFT, TextAlign.CENTER, TextAlign.RIGHT):
        for valign in (VerticalAlign.TOP, VerticalAlign.MIDDLE, VerticalAlign.BOTTOM):
            for outside in (True, False):
                align = (halign, valign)
                point_expected = data[(halign, valign, outside)]
                point = get_text_point(extents, 160, 40, align, padding, outside)

                assert point[0] == point_expected[0], "%s, %s -> %s" % (
                    align,
                    outside,
                    point[0],
                )
                assert point[1] == point_expected[1], "%s, %s -> %s" % (
                    align,
                    outside,
                    point[1],
                )
