from __future__ import annotations

from typing import Callable, Dict, Generator, List, Optional, Tuple, Union

import tinycss2
from cssselect2.compiler import CompiledSelector, compile_selector_list
from cssselect2.parser import SelectorError
from typing_extensions import Literal


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


def parse_stylesheet(
    css,
) -> Generator[
    Union[
        Tuple[CompiledSelector, Dict[str, object]],
        Tuple[Literal["error"], Union[tinycss2.ast.ParseError, SelectorError]],
    ],
    None,
    None,
]:
    rules = tinycss2.parse_stylesheet(
        css or "", skip_comments=True, skip_whitespace=True
    )
    for rule in rules:
        if rule.type == "error":
            yield ("error", rule)
            continue
        try:
            selectors = compile_selector_list(rule.prelude)
        except SelectorError as e:
            yield ("error", e)
            continue

        yield (
            selectors,
            {
                prop: value
                for prop, value in (
                    (prop, StyleDeclarations(prop, value))
                    for prop, value in parse_declarations(rule)
                )
                if value is not None
            },
        )


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
            raise ValueError(f"Can not handle node type {token.type}")

    if state == VALUE and value:
        yield (name, value[0] if len(value) == 1 else tuple(value))
