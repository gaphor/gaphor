from typing import Dict, Optional, Sequence, Tuple, Union

import tinycss2.color3
from typing_extensions import TypedDict

from gaphor.core.styling import StyleDeclarations
from gaphor.diagram.text import (
    FontStyle,
    FontWeight,
    TextAlign,
    TextDecoration,
    VerticalAlign,
)

Color = Tuple[float, float, float, float]  # RGBA
Padding = Tuple[float, float, float, float]  # top/right/bottom/left
Number = Union[int, float]

# Style is using SVG properties where possible
# https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute
Style = TypedDict(
    "Style",
    {
        "padding": Padding,
        "min-width": Number,
        "min-height": Number,
        "line-width": Number,
        "vertical-spacing": Number,
        "border-radius": Number,
        "background-color": Color,
        "font-family": str,
        "font-size": Number,
        "font-style": FontStyle,
        "font-weight": FontWeight,
        "text-decoration": TextDecoration,
        "text-align": TextAlign,
        "text-color": Color,
        "color": Color,
        "vertical-align": VerticalAlign,
        "dash-style": Sequence[Number],
        "highlight-color": Color,
    },
    total=False,
)

number = (int, float)


def _clip_color(c):
    if c < 0:
        return 0
    if c > 1:
        return 1
    return c


@StyleDeclarations.register(
    "background-color", "color", "highlight-color", "text-color"
)
def parse_color(prop, value):
    color = tinycss2.color3.parse_color(value)
    return tuple(_clip_color(v) for v in color) if color else None


@StyleDeclarations.register(
    "min-width",
    "min-height",
    "line-width",
    "vertical-spacing",
    "border-radius",
    "font-size",
)
def parse_positive_number(prop, value) -> Optional[Number]:
    if isinstance(value, number) and value > 0:
        return value
    return None


@StyleDeclarations.register("font-family")
def parse_string(prop, value) -> Optional[str]:
    if isinstance(value, str):
        return value
    elif value:
        return " ".join(str(v) for v in value)
    return None


@StyleDeclarations.register("padding")
def parse_padding(prop, value) -> Optional[Padding]:
    if isinstance(value, number):
        return (value, value, value, value)
    n = len(value)
    if not n or any(not isinstance(v, number) for v in value):
        return None

    return (
        value[0],
        value[1],
        value[2] if n > 2 else value[0],
        value[3] if n > 3 else value[1],
    )


@StyleDeclarations.register("dash-style")
def parse_sequence_numbers(
    prop, value: Union[Number, Sequence[Number]]
) -> Optional[Sequence[Number]]:
    if isinstance(value, number):
        return (value, value)
    elif all(isinstance(v, (int, float)) for v in value):
        return value
    return None


enum_styles: Dict[str, Dict[str, object]] = {
    "font-style": {e.value: e for e in FontStyle},
    "font-weight": {e.value: e for e in FontWeight},
    "text-decoration": {e.value: e for e in TextDecoration},
    "text-align": {e.value: e for e in TextAlign},
    "vertical-align": {e.value: e for e in VerticalAlign},
}


@StyleDeclarations.register(*enum_styles.keys())
def parse_enum(prop, value):
    return enum_styles[prop].get(value)
