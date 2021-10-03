"""Definitions (types) for style sheets."""
from enum import Enum
from typing import Sequence, Tuple, TypedDict, Union

Color = Tuple[float, float, float, float]  # RGBA
Padding = Tuple[float, float, float, float]  # top/right/bottom/left
Number = Union[int, float]


class TextAlign(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlign(Enum):
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


class FontStyle(Enum):
    NORMAL = "normal"
    ITALIC = "italic"


class FontWeight(Enum):
    NORMAL = "normal"
    BOLD = "bold"


class TextDecoration(Enum):
    NONE = "none"
    UNDERLINE = "underline"


# Style is using SVG properties where possible
# https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute
Style = TypedDict(
    "Style",
    {
        "background-color": Color,
        "border-radius": Number,
        "color": Color,
        "dash-style": Sequence[Number],
        "padding": Padding,
        "font-family": str,
        "font-size": Union[int, float, str],
        "font-style": FontStyle,
        "font-weight": FontWeight,
        "line-style": Number,
        "line-width": Number,
        "min-width": Number,
        "min-height": Number,
        "opacity": Number,
        "text-decoration": TextDecoration,
        "text-align": TextAlign,
        "text-color": Color,
        "vertical-align": VerticalAlign,
        "vertical-spacing": Number,
    },
    total=False,
)
