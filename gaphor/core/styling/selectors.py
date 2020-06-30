import re
from functools import singledispatch

from cssselect2 import parser
from cssselect2.parser import SelectorError

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
