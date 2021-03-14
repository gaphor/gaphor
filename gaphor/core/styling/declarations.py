from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

import tinycss2.color3
from tinycss2.parser import parse_declaration_list

from gaphor.core.styling.properties import (
    FontStyle,
    FontWeight,
    Number,
    Padding,
    TextAlign,
    TextDecoration,
    VerticalAlign,
)

FONT_SIZE_VALUES = {
    "x-small": 3 / 4,
    "small": 8 / 9,
    "medium": 1,
    "large": 6 / 5,
    "x-large": 3 / 2,
}


class _Declarations:
    """Convert raw CSS declarations into Gaphor styling declarations."""

    def __init__(self) -> None:
        self.declarations: List[
            Tuple[str, Callable[[str, object], Optional[object]]]
        ] = []

    def register(self, *properties):
        def reg(func):
            for prop in properties:
                self.declarations.append((prop, func))
            return func

        return reg

    def __call__(self, property, value):
        for prop, func in self.declarations:
            if property == prop:
                return func(property, value)


declarations = _Declarations()


def parse_declarations(declaration_list):

    for decl in parse_declaration_list(
        declaration_list, skip_comments=True, skip_whitespace=True
    ):
        if decl.type == "declaration":
            name = decl.lower_name
            yield (
                name,
                declarations(name, parse_value(decl.value)),
            )
        elif decl.type == "error":
            yield "error", decl


def parse_value(tokens):
    value = []

    for token in tokens:
        if token.type in ("whitespace", "comment"):
            pass
        elif token.type in ("ident", "string"):
            value.append(token.value)
        elif token.type in ("dimension", "number"):
            value.append(token.int_value if token.is_integer else token.value)
        elif token.type == "hash":
            value.append("#" + token.value)
        elif token.type == "function":
            value.append(token)
        else:
            value.append(token.serialize())

    return value[0] if len(value) == 1 else tuple(value)


number = (int, float)


def _clip_color(c):
    if c < 0:
        return 0
    if c > 1:
        return 1
    return c


@declarations.register("background-color", "color", "text-color")
def parse_color(prop, value):
    try:
        color = tinycss2.color3.parse_color(value)
    except AttributeError:
        return None
    return tuple(_clip_color(v) for v in color) if color else None


@declarations.register(
    "min-width",
    "min-height",
    "line-width",
    "vertical-spacing",
    "border-radius",
)
def parse_positive_number(prop, value) -> Optional[Number]:
    if isinstance(value, number) and value >= 0:
        return value
    return None


@declarations.register(
    "opacity",
)
def parse_factor(prop, value) -> Optional[Number]:
    if isinstance(value, number) and 0 <= value <= 1:
        return value
    return None


@declarations.register("font-family")
def parse_string(prop, value) -> Optional[str]:
    if isinstance(value, str):
        return value
    elif value:
        return " ".join(str(v) for v in value)
    return None


@declarations.register("font-size")
def parse_font_size(prop, value) -> Union[None, int, float, str]:
    if isinstance(value, number) and value > 0:
        return value
    if isinstance(value, str) and value in FONT_SIZE_VALUES:
        return value
    return None


@declarations.register("padding")
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


@declarations.register("dash-style")
def parse_sequence_numbers(
    prop, value: Union[Number, Sequence[Number]]
) -> Optional[Sequence[Number]]:
    if value == 0:
        return ()
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


@declarations.register(*enum_styles.keys())
def parse_enum(prop, value):
    return enum_styles[prop].get(value)


@declarations.register("line-style")
def parse_line_style(prop, value) -> float:
    if value == "sloppy":
        return 0.5
    elif isinstance(value, tuple) and len(value) == 2:
        style, factor = value
        if style == "sloppy":
            if not isinstance(factor, number):
                return 0.5
            if factor < -2.0:
                return -2.0
            elif factor > 2.0:
                return 2.0
            else:
                return float(factor)
    # "normal" value:
    return 0.0
