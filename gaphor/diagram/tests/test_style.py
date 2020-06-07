import pytest

import gaphor.diagram.style
from gaphor.core.styling import parse_stylesheet
from gaphor.diagram.text import FontWeight


def first_decl_block(css):
    prop, value = next(parse_stylesheet(css))
    return value


@pytest.mark.parametrize(
    "color,rgba",
    [
        ["red", (1, 0, 0, 1)],
        ["#00ff00", (0, 1, 0, 1)],
        ["rgb(0, 255, 0)", (0, 1, 0, 1)],
        ["rgba(0, 255, 0, 0.3)", (0, 1, 0, 0.3)],
        ["rgb(0, 300, 0)", (0, 1, 0, 1)],
        ["gred", None],
        ["#00fg00", None],
        ["#00fg0000", None],
    ],
)
def test_color_parsing(color, rgba):
    css = f"* {{ color: {color}; }}"
    props = first_decl_block(css)

    if rgba is None:
        assert "color" not in props
    else:
        assert tuple(props["color"]) == rgba


def test_negative_number():
    css = "* { min-width: -1; }"
    props = first_decl_block(css)

    assert "min-width" not in props


def test_not_a_number():
    css = "* { min-width: foo; }"
    props = first_decl_block(css)

    assert "min-width" not in props


@pytest.mark.parametrize(
    "padding,expected",
    [
        [0, (0, 0, 0, 0)],
        [3, (3, 3, 3, 3)],
        ["1 3", (1, 3, 1, 3)],
        ["1 2 3", (1, 2, 3, 2)],
        ["1 2 3 4", (1, 2, 3, 4)],
        ["foo", None],
        ["", None],
    ],
)
def test_padding(padding, expected):
    css = f"* {{ padding: {padding}; }}"
    props = first_decl_block(css)

    assert props.get("padding") == expected


def test_enum_style():
    css = "* { font-weight: bold; }"
    props = first_decl_block(css)

    from gaphor.core.styling import StyleDeclarations

    print(StyleDeclarations.declarations)
    assert props["font-weight"] == FontWeight.BOLD
