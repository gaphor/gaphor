from __future__ import annotations

from typing import Callable, Dict, Generator, List, Optional, Tuple, Union

import tinycss2

Selector = Tuple[tinycss2.ast.Node]


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


def parse_stylesheet(css) -> Generator[Tuple[Selector, Dict[str, object]], None, None]:
    rules = tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True)
    return (
        (
            rule.prelude,
            {
                prop: value
                for prop, value in (
                    (prop, StyleDeclarations(prop, value))
                    for prop, value in parse_declarations(rule)
                )
                if value is not None
            },
        )
        for rule in rules
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
        elif token.type == "literal" and token.value == ";":
            yield (name, value[0] if len(value) == 1 else tuple(value))
            state = NAME
        elif token.type in ("whitespace", "comment"):
            pass
        elif token.type in ("ident", "string"):
            if state == NAME:
                name = token.value
            elif state == VALUE:
                value.append(token.value)
        elif token.type in ("dimension", "number"):
            assert state == VALUE
            value.append(token.value)
        elif token.type == "hash":
            assert state == VALUE
            value.append("#" + token.value)
        elif token.type == "function":
            assert state == VALUE
            value.append(token)
        else:
            raise ValueError(f"Can not handle node type {token.type}")
