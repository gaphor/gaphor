from __future__ import annotations

import operator
import re
from functools import reduce, singledispatch
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

import tinycss2
from cssselect2 import parser
from typing_extensions import Literal
from webencodings import ascii_lower

MATCH_SORT_KEY = operator.itemgetter(0, 1)


def merge_styles(styles) -> Dict[str, object]:
    style = {}
    for s in styles:
        style.update(s)
    return style


class CompiledStyleSheet:
    def __init__(self, css):
        self.selectors = [
            (selspec[0], selspec[1], order, declarations)
            for order, (selspec, declarations) in enumerate(parse_style_sheet(css))
            if selspec != "error"
        ]

    def match(self, element) -> Dict[str, object]:
        results = sorted(
            (
                (specificity, order, declarations)
                for pred, specificity, order, declarations in self.selectors
                if pred(element)
            ),
            key=MATCH_SORT_KEY,
        )
        return merge_styles(decl for _, _, decl in results)


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


def parse_style_sheet(
    css,
) -> Generator[
    Union[
        Tuple[Tuple[Callable[[object], bool], Tuple[int, int, int]], Dict[str, object]],
        Tuple[Literal["error"], Union[tinycss2.ast.ParseError, parser.SelectorError]],
    ],
    None,
    None,
]:
    rules = tinycss2.parse_stylesheet(
        css or "", skip_comments=True, skip_whitespace=True
    )
    for rule in rules:
        if rule.type == "error":
            assert isinstance(rule, tinycss2.ast.ParseError)
            yield ("error", rule)  # type: ignore[misc]
            continue
        try:
            selectors = compile_selector_list(rule.prelude)
        except parser.SelectorError as e:
            yield ("error", e)  # type: ignore[misc]
            continue

        declaration = {
            prop: value
            for prop, value in (
                (prop, StyleDeclarations(prop, value))
                for prop, value in parse_declarations(rule)
            )
            if value is not None
        }

        yield from ((selector, declaration) for selector in selectors)


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


# http://dev.w3.org/csswg/selectors/#whitespace
split_whitespace = re.compile("[^ \t\r\n\f]+").findall


def compile_selector_list(input):
    """
    Compile a (comma-separated) list of selectors.

    Based on cssselect2.compiler.compile_selector_list().

    Returns a list of compiled selectors.
    """
    return [
        (compile_node(selector.parsed_tree), selector.specificity)
        for selector in parser.parse(input)
    ]


@singledispatch
def compile_node(selector):
    """
    Dynamic dispatch selector nodes.

    Default behavior is a deny (no match).
    """
    print("selector", type(selector))
    return lambda el: False


@compile_node.register
def compile_compound_selector(selector: parser.CompoundSelector):
    sub_expressions = [compile_node(sel) for sel in selector.simple_selectors]
    return lambda el: all(expr(el) for expr in sub_expressions)


@compile_node.register
def compile_local_name_selector(selector: parser.LocalNameSelector):
    return lambda el: el.local_name() == selector.lower_local_name


def ancestors(el):
    p = el.parent()
    if p:
        yield p
        yield from ancestors(p)


def descendants(el):
    for c in el.children():
        yield c
        yield from descendants(c)


@compile_node.register
def compile_combined_selector(selector: parser.CombinedSelector):
    left_inside = compile_node(selector.left)
    if selector.combinator == " ":

        def left(el):
            return any(left_inside(e) for e in ancestors(el))

    elif selector.combinator == ">":

        def left(el):
            p = el.parent()
            return p is not None and left_inside(p)

    else:
        raise parser.SelectorError("Unknown combinator", selector.combinator)

    right = compile_node(selector.right)
    return lambda el: right(el) and left(el)


@compile_node.register
def compile_functional_pseudo_class_selector(
    selector: parser.FunctionalPseudoClassSelector,
):
    if selector.name == "has":
        embedded_selectors = compile_selector_list(selector.arguments)

        return lambda el: any(
            any(sel(c) for sel, _ in embedded_selectors) for c in descendants(el)
        )
    else:
        raise parser.SelectorError("Unknown pseudo-class", selector.name)


@compile_node.register
def compile_attribute_selector(selector: parser.AttributeSelector):
    name = selector.name
    operator = selector.operator
    value = selector.value

    if operator is None:
        return lambda el: bool(el.attribute(name))
    elif operator == "=":
        return lambda el: el.attribute(name) == value
    elif operator == "~=":
        return lambda el: value in split_whitespace(el.attribute(name))
    elif selector.operator == "|=":

        def pipe_equal_matcher(el):
            v = el.attribute(name)
            return v == value or (v and v.startswith(value + "-"))

        return pipe_equal_matcher
    elif selector.operator == "^=":
        return lambda el: value and el.attribute(name).startswith(value)
    elif selector.operator == "$=":
        return lambda el: value and el.attribute(name).endswith(value)
    elif selector.operator == "*=":
        return lambda el: value and value in el.attribute(name)
    else:
        raise parser.SelectorError("Unknown attribute operator", selector.operator)
