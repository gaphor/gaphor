import pytest

from gaphor.core.styling import merge_styles
from gaphor.core.styling.declarations import Var


def test_merge_opacity():
    style = merge_styles({"color": (0, 0, 1, 1), "opacity": 0.7})

    assert style["color"] == (0, 0, 1, 0.7)


def test_merge_opacity_with_transparent():
    style = merge_styles({"color": (0, 0, 0, 0), "opacity": 0.7})

    assert style["color"] == (0, 0, 0, 0)


def test_merge_opacity_with_transparency():
    style = merge_styles({"color": (0, 0, 0, 0.8), "opacity": 0.5})

    assert style["color"] == (0, 0, 0, 0.4)


@pytest.mark.parametrize(
    "font_size,factor",
    [
        ["x-small", 3 / 4],
        ["small", 8 / 9],
        ["medium", 1],
        ["large", 6 / 5],
        ["x-large", 3 / 2],
    ],
)
def test_font_size(font_size, factor):
    style = merge_styles({"font-size": 10}, {"font-size": font_size})

    assert style["font-size"] == 10 * factor


def test_final_font_size_is_a_number():
    style = merge_styles({"font-size": 10}, {"font-size": "x-small"}, {"font-size": 24})

    assert style["font-size"] == 24


def test_font_size_override_with_relative_size():
    style = merge_styles({"font-size": 10}, {"font-size": 24}, {"font-size": "x-small"})

    assert style["font-size"] == 24 * 3 / 4


def test_color_override_with_variables():
    style = merge_styles(
        {"--my-color": "white", "--my-opacity": 0.5},
        {"color": Var("--my-color"), "opacity": Var("--my-opacity")},
    )

    assert style["color"] == (1.0, 1.0, 1.0, 0.5)
