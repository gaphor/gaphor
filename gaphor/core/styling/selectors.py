"""Compiler for CSS selectors, based on cssselect2.compiler, written by Simon
Sapin and Guillaume Ayoub."""

import re
from functools import singledispatch

from gaphor.core.styling import parser

# http://dev.w3.org/csswg/selectors/#whitespace
split_whitespace = re.compile("[^ \t\r\n\f]+").findall


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

    Default behavior is a deny (no match).
    """
    raise parser.SelectorError("Unknown selector", selector)


@compile_node.register
def compile_compound_selector(selector: parser.CompoundSelector):
    sub_expressions = [compile_node(sel) for sel in selector.simple_selectors]
    return lambda el: all(expr(el) for expr in sub_expressions)


@compile_node.register
def compile_name_selector(selector: parser.LocalNameSelector):
    return lambda el: el.name() == selector.lower_local_name


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
            return v == value or (v and v.startswith(value + "-"))

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
