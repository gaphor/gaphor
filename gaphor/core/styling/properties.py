"""
Definitions (types) for style sheets.

"""
from enum import Enum
from typing import Sequence, Tuple, Union

from typing_extensions import TypedDict

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
        "line-style": Number,
    },
    total=False,
)
