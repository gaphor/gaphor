from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

import tinycss2.color3

from gaphor.core.styling.properties import (
    FontStyle,
    FontWeight,
    Number,
    Padding,
    TextAlign,
    TextDecoration,
    VerticalAlign,
)


class _StyleDeclarations:
    """
    Convert raw CSS declarations into Gaphor styling declarations.
    """

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


StyleDeclarations = _StyleDeclarations()


def parse_declarations(rule):
    NAME = 0
    VALUE = 1

    if rule.type != "qualified-rule":
        return

    state = NAME
    name: Optional[str] = None
    value: List[Union[str, float]] = []
    for token in rule.content:
        if token.type == "literal" and token.value == ":":
            state = VALUE
        elif (token.type == "literal" and token.value == ";") or (
            name and value and token.type == "whitespace" and "\n" in token.value
        ):
            yield (name, value[0] if len(value) == 1 else tuple(value))
            state = NAME
            name = None
            value = []
        elif token.type in ("whitespace", "comment"):
            pass
        elif token.type in ("ident", "string"):
            if state == NAME:
                name = token.value
            elif state == VALUE:
                value.append(token.value)
        elif token.type in ("dimension", "number"):
            assert state == VALUE
            value.append(token.int_value if token.is_integer else token.value)
        elif token.type == "hash":
            assert state == VALUE
            value.append("#" + token.value)
        elif token.type == "function":
            assert state == VALUE
            value.append(token)
        else:
            value.append(token.serialize())

    if state == VALUE and value:
        yield (name, value[0] if len(value) == 1 else tuple(value))


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
    try:
        color = tinycss2.color3.parse_color(value)
    except AttributeError:
        return None
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
