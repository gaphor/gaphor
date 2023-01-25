"""Compiler for CSS selectors.

Based on cssselect2.compiler, written by Simon Sapin and Guillaume
Ayoub.
"""

import re
from functools import singledispatch
from typing import Callable, Dict, Iterator, Literal, Tuple, Union

import tinycss2

from gaphor.core.styling import parser
from gaphor.core.styling.declarations import parse_declarations

# http://dev.w3.org/csswg/selectors/#whitespace
split_whitespace = re.compile("[^ \t\r\n\f]+").findall


Rule = Union[
    Tuple[Tuple[Callable[[object], bool], Tuple[int, int, int]], Dict[str, object]],
    Tuple[Literal["error"], Union[tinycss2.ast.ParseError, parser.SelectorError]],
]


def compile_style_sheet(*css: str) -> Iterator[Rule]:
    for sheet in css:
        if sheet:
            rules = tinycss2.parse_stylesheet(
                sheet, skip_comments=True, skip_whitespace=True
            )
            yield from compile_rules(rules)


def compile_rules(rules):
    for rule in rules:
        if rule.type == "error":
            yield "error", rule
            continue

        if rule.type == "at-rule":
            at_rules = tinycss2.parser.parse_rule_list(
                rule.content, skip_comments=True, skip_whitespace=True
            )
            media_selector = parser.parse_media_query(rule.prelude)
            if not media_selector:
                continue
            media_query = compile_node(media_selector)
            yield from (
                ((_combine(media_query, selector), specificity), declaration)
                for (selector, specificity), declaration in compile_rules(at_rules)
            )

        if rule.type != "qualified-rule":
            continue

        try:
            selectors = compile_selector_list(rule.prelude)
        except parser.SelectorError as e:
            yield "error", e
            continue

        declaration = {
            prop: value
            for prop, value in parse_declarations(rule.content)
            if prop != "error" and value is not None
        }

        yield from ((selector, declaration) for selector in selectors)


def _combine(a, b):
    return lambda el: a(el) and b(el)


def compile_selector_list(input):
    """Compile a (comma-separated) list of selectors.

    Based on cssselect2.compiler.compile_selector_list().

    Returns a list of compiled selectors.
    """
    return [
        (compile_node(selector), selector.specificity)
        for selector in parser.parse(input)
    ]


@singledispatch
def compile_node(selector):
    """Dynamic dispatch selector nodes.

    Default behavior is to deny (no match).
    """
    raise parser.SelectorError("Unknown selector", selector)


@compile_node.register
def compile_media_selector(selector: parser.MediaSelector):
    feature = selector.feature.lower()
    operator = selector.operator
    value = selector.value.lower()
    if feature == "prefers-color-scheme" and operator == "=":
        return lambda el: el.color_scheme() == value
    return lambda el: False


@compile_node.register
def compile_compound_selector(selector: parser.CompoundSelector):
    sub_expressions = [compile_node(sel) for sel in selector.simple_selectors]
    return lambda el: all(expr(el) for expr in sub_expressions)


@compile_node.register
def compile_name_selector(selector: parser.LocalNameSelector):
    return lambda el: el.name() == selector.lower_local_name


def ancestors(el):
    if p := el.parent():
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
def compile_attribute_selector(selector: parser.AttributeSelector):
    name = selector.lower_name
    operator = selector.operator
    value = selector.value and selector.value.lower()

    if operator is None:
        return lambda el: bool(el.attribute(name))
    elif operator == "=":
        return lambda el: el.attribute(name) == value
    elif operator == "~=":
        return lambda el: value in split_whitespace(el.attribute(name))
    elif operator == "^=":
        return lambda el: value and el.attribute(name).startswith(value)
    elif operator == "$=":
        return lambda el: value and el.attribute(name).endswith(value)
    elif operator == "*=":
        return lambda el: value and value in el.attribute(name)
    elif operator == "|=":

        def pipe_equal_matcher(el):
            v = el.attribute(name)
            return v == value or v and v.startswith(f"{value}-")

        return pipe_equal_matcher
    else:
        raise parser.SelectorError("Unknown attribute operator", operator)


@compile_node.register
def compile_pseudo_class_selector(selector: parser.PseudoClassSelector):
    name = selector.name
    if name == "empty":
        return lambda el: not next(el.children(), 0)
    elif name in ("root", "hover", "focus", "active", "drop", "disabled"):
        return lambda el: name in el.state()
    else:
        raise parser.SelectorError("Unknown pseudo-class", name)


@compile_node.register
def compile_functional_pseudo_class_selector(
    selector: parser.FunctionalPseudoClassSelector,
):
    name = selector.name
    if name not in ("has", "is", "not"):
        raise parser.SelectorError("Unknown pseudo-class", name)

    sub_selectors = compile_selector_list(selector.arguments)
    selector.specificity = max(spec for _, spec in sub_selectors)
    if name == "has":
        return lambda el: any(
            any(sel(c) for sel, _ in sub_selectors) for c in descendants(el)
        )
    elif name == "is":
        return lambda el: any(sel(el) for sel, _ in sub_selectors)
    elif name == "not":
        return lambda el: not any(sel(el) for sel, _ in sub_selectors)
