from typing import Callable, List, Optional, Tuple, Union

import tinycss2


class _StyleDeclarations:
    """
    Convert raw CSS declarations into Gaphor styling declarations.
    """

    def __init__(self) -> None:
        self.declarations: List[Tuple[str, Callable[[str, object], object]]] = []

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


def parse_stylesheet(css):
    rules = tinycss2.parse_stylesheet(css, skip_whitespace=True)
    for rule in rules:
        return {
            prop: StyleDeclarations(prop, value)
            for prop, value in parse_declarations(rule)
        }


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
            # TODO: dispatch on name to validate content (string, number, tuple)
            yield (name, value[0] if len(value) == 1 else tuple(value))
            state = NAME
        elif token.type == "whitespace":
            pass
        elif token.type in ("ident", "number", "string"):
            if state == NAME:
                name = token.value
            elif state == VALUE:
                value.append(token.value)
        else:
            raise ValueError(f"Can now handle node type {token.type}")
