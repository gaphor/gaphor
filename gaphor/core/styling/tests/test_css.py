import cssselect2
import pytest
import tinycss2


def parse_rule_content(rule):
    NAME = 0
    VALUE = 1

    if rule.type != "qualified-rule":
        return

    state = NAME
    name = None
    value = []
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


def test_css_content_for_integer():
    css = """
    * {
        font-size: 42;
    }
    """
    rules = tinycss2.parse_stylesheet(css, skip_whitespace=True)

    n, v = next(parse_rule_content(rules[0]))

    assert n == "font-size"
    assert v == 42


def test_css_content_for_string():
    css = """
    * {
        font-family: 'sans';
    }
    """
    rules = tinycss2.parse_stylesheet(css, skip_whitespace=True)

    n, v = next(parse_rule_content(rules[0]))

    assert n == "font-family"
    assert v == "sans"


def test_css_content_for_ident():
    css = """
    * {
        font-family: sans;
    }
    """
    rules = tinycss2.parse_stylesheet(css, skip_whitespace=True)

    n, v = next(parse_rule_content(rules[0]))

    assert n == "font-family"
    assert v == "sans"


def test_css_content_for_tuple():
    css = """
    * {
        padding: 1 2 3 4;
    }
    """
    rules = tinycss2.parse_stylesheet(css, skip_whitespace=True)

    n, v = next(parse_rule_content(rules[0]))

    assert n == "padding"
    assert v == (1.0, 2.0, 3.0, 4.0)


def test_css_for_item(element_factory, diagram):
    css = """
    ClassItem {
        font-size: 42;
        font-family: "sans";

    }
    """
    rules = tinycss2.parse_stylesheet(css, skip_whitespace=True)

    for rule in rules:
        selectors = cssselect2.compile_selector_list(rule.prelude)
        print(selectors)
        selector_string = tinycss2.serialize(rule.prelude)
        content_string = tinycss2.serialize(rule.content)
        print(rule.content)
        payload = (selector_string, content_string)
        print(payload)
        # for selector in selectors:
        #     matcher.add_selector(selector, payload)

    assert 0
