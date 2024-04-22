"""Compiler for CSS selectors.

Based on cssselect2.compiler, written by Simon Sapin and Guillaume
Ayoub.
"""

import re
from functools import singledispatch
from typing import Callable, Dict, Iterator, Literal, Tuple, Union

import tinycss2

from gaphor.core.styling import selectors
from gaphor.core.styling.declarations import parse_declarations

# http://dev.w3.org/csswg/selectors/#whitespace
split_whitespace = re.compile("[^ \t\r\n\f]+").findall


Rule = Union[
    Tuple[Callable[[object], bool], Dict[str, object]],
    Tuple[Literal["error"], Union[tinycss2.ast.ParseError, selectors.SelectorError]],
]


def compile_style_sheet(*css: str) -> Iterator[Rule]:
    return (
        compiled_rule
        for _specificity, _order, compiled_rule in sorted(
            (
                ((-1,), order, (selspec, declarations))
                if selspec == "error"
                else (selspec[1], order, (selspec[0], declarations))
            )
            for order, (selspec, declarations) in enumerate(
                rule
                for sheet in css
                for rule in compile_rules(
                    tinycss2.parse_stylesheet(
                        sheet, skip_comments=True, skip_whitespace=True
                    )
                )
                if sheet
            )
        )
    )


def compile_rules(rules):
    for rule in rules:
        if rule.type == "error":
            yield "error", rule
            continue

        if rule.type == "at-rule" and rule.content:
            at_rules = tinycss2.parser.parse_rule_list(
                rule.content, skip_comments=True, skip_whitespace=True
            )
            media_selector = selectors.media_query_selector(rule.prelude)
            if not media_selector:
                continue
            media_query = compile_node(media_selector)
            yield from (
                ((_combine(media_query, selspec[0]), selspec[1]), declaration)
                for selspec, declaration in compile_rules(at_rules)
                if selspec != "error"
            )

        if rule.type != "qualified-rule":
            continue

        try:
            selector_list = compile_selector_list(rule.prelude)
        except selectors.SelectorError as e:
            yield "error", e
            continue

        declaration = {
            prop: value
            for prop, value in parse_declarations(rule.content)
            if prop != "error" and value is not None
        }

        yield from ((selector, declaration) for selector in selector_list)


def _combine(a, b):
    return lambda el: a(el) and b(el)


def compile_selector_list(input):
    """Compile a (comma-separated) list of selectors.

    Based on cssselect2.compiler.compile_selector_list().

    Returns a list of compiled selectors.
    """
    return [
        (compile_node(selector), selector.specificity)
        for selector in selectors.selectors(input)
    ]


@singledispatch
def compile_node(selector):
    """Dynamic dispatch selector nodes.

    Default behavior is to deny (no match).
    """
    raise selectors.SelectorError("Unknown selector", selector)


@compile_node.register
def compile_media_selector(selector: selectors.MediaSelector):
    query = selector.query
    if len(query) == 1:
        mode = query[0].lower()
    elif (
        len(query) == 3
        and query[0].lower() == "prefers-color-scheme"
        and query[1] == "="
    ):
        mode = query[2].lower()
    else:
        mode = None

    if mode in ("dark", "dark-mode"):
        return lambda el: el.dark_mode is True
    elif mode in ("light", "light-mode"):
        return lambda el: el.dark_mode is False
    return lambda el: False


@compile_node.register
def compile_compound_selector(selector: selectors.CompoundSelector):
    sub_expressions = [compile_node(sel) for sel in selector.simple_selectors]
    return lambda el: all(expr(el) for expr in sub_expressions)


@compile_node.register
def compile_name_selector(selector: selectors.LocalNameSelector):
    return lambda el: el.name() == selector.lower_local_name


def ancestors(el):
    if p := el.parent():
        yield p
        yield from ancestors(p)


def descendants(el):
    for c in el.children():
        yield c
        yield from descendants(c)


def previous(el):
    p = el.parent()
    if p is None:
        return None
    children = list(p.children())
    try:
        i = children.index(el)
    except ValueError:
        return None

    return None if i == 0 else children[i - 1]


@compile_node.register
def compile_combined_selector(selector: selectors.CombinedSelector):
    left_inside = compile_node(selector.left)
    if selector.combinator == " ":

        def left(el):
            return any(left_inside(e) for e in ancestors(el))

    elif selector.combinator == ">":

        def left(el):
            p = el.parent()
            return p is not None and left_inside(p)

    elif selector.combinator == "+":

        def left(el):
            p = previous(el)
            return p is not None and left_inside(p)

    else:
        raise selectors.SelectorError("Unknown combinator", selector.combinator)

    right = compile_node(selector.right)
    return lambda el: right(el) and left(el)


@compile_node.register
def compile_attribute_selector(selector: selectors.AttributeSelector):
    name = selector.lower_name
    operator = selector.operator
    value = selector.value and selector.value.lower()

    if operator is None:
        return lambda el: bool(el.attribute(name))
    elif operator == "=":
        return lambda el: el.attribute(name) == value
    elif operator == "~=":
        return lambda el: (
            attr := el.attribute(name)
        ) is not None and value in split_whitespace(attr)
    elif operator == "^=":
        return (
            lambda el: value
            and (attr := el.attribute(name)) is not None
            and attr.startswith(value)
        )
    elif operator == "$=":
        return (
            lambda el: value
            and (attr := el.attribute(name)) is not None
            and attr.endswith(value)
        )
    elif operator == "*=":
        return (
            lambda el: value
            and (attr := el.attribute(name)) is not None
            and value in attr
        )
    elif operator == "|=":

        def pipe_equal_matcher(el):
            v = el.attribute(name)
            return v == value or v and v.startswith(f"{value}-")

        return pipe_equal_matcher
    else:
        raise selectors.SelectorError("Unknown attribute operator", operator)


@compile_node.register
def compile_pseudo_class_selector(selector: selectors.PseudoClassSelector):
    name = selector.name
    if name == "empty":
        return lambda el: not next(el.children(), 0)
    elif name == "root":
        return lambda el: not el.parent()
    elif name in ("hover", "focus", "active", "drop", "disabled"):
        return lambda el: name in el.state()
    elif name == "first-child":
        return lambda el: previous(el) is None
    else:
        raise selectors.SelectorError("Unknown pseudo-class", name)


@compile_node.register
def compile_functional_pseudo_class_selector(
    selector: selectors.FunctionalPseudoClassSelector,
):
    name = selector.name
    if name not in ("has", "is", "not"):
        raise selectors.SelectorError("Unknown pseudo-class", name)

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


@compile_node.register
def compile_pseudo_element_selector(selector: selectors.PseudoElementSelector):
    name = selector.name
    if name != "after":
        raise selectors.SelectorError("Unknown pseudo-element", name)

    return lambda el: name == el.pseudo
