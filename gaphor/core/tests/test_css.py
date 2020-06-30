import cssselect2
import pytest
import tinycss2

from gaphor.core.styling import CompiledStyleSheet, StyleDeclarations, parse_style_sheet
from gaphor.core.tests.test_selector import SelectorProperties


def first_decl_block(css):
    _, value = next(parse_style_sheet(css))
    return value


@StyleDeclarations.register("test-padding", "test-font-size", "test-font-family")
def dummy_style_declaration(prop, value):
    return value


def test_empty_css():
    css = ""
    rules = list(parse_style_sheet(css))

    assert rules == []


def test_css_content_for_integer():
    css = """
    * {
        test-font-size: 42;
    }
    """
    props = first_decl_block(css)

    assert props["test-font-size"] == 42


def test_css_content_for_string():
    css = """
    * {
        test-font-family: 'sans';
    }
    """
    props = first_decl_block(css)

    assert props["test-font-family"] == "sans"


def test_css_content_for_ident():
    css = """
    * {
        test-font-family: sans;
    }
    """
    props = first_decl_block(css)

    assert props["test-font-family"] == "sans"


def test_css_content_for_tuple():
    css = """
    * {
        test-padding: 1 2 3 4;
    }
    """
    props = first_decl_block(css)

    assert props["test-padding"] == (1.0, 2.0, 3.0, 4.0)


def test_multiple_rules():
    css = """
    * {}
    item {}
    """

    rules = list(parse_style_sheet(css))

    assert len(rules) == 2


def test_selectors():
    css = """
    foo, bar {}
    """
    selector, declarations = next(parse_style_sheet(css))

    assert len(selector) == 2


def test_invalid_css_syntax():
    css = """
    foo/bar ;
    """
    rules = list(parse_style_sheet(css))
    selector, _ = rules[0]

    assert len(rules) == 1
    assert selector == "error"


def test_invalid_css_syntax_in_declarations():
    css = """
    foo { foo : bar : baz }
    """
    rules = list(parse_style_sheet(css))
    _, decls = rules[0]

    assert len(rules) == 1
    assert len(decls) == 0


def test_invalid_selector():
    css = """
    foo/bar {}
    good {}
    """
    rules = list(parse_style_sheet(css))
    selector, _ = rules[0]

    assert len(rules) == 2
    assert selector == "error"


def test_css_declaration_without_semicolumn():
    css = """
    * {
        test-font-family: 'sans'
    }
    """
    props = first_decl_block(css)

    assert props.get("test-font-family") == "sans"


def test_css_multiple_declarations_without_semicolumns():
    css = """
    * {
        test-font-family: sans
        test-font-size: 42
    }
    """
    props = first_decl_block(css)

    assert props.get("test-font-family") == "sans"
    assert props.get("test-font-size") == 42


def test_compiled_style_sheet():
    css = """
    * {
        test-font-size: 42
        test-font-family: overridden
    }
    mytype {
        test-font-family: sans
    }
    """

    compiled_style_sheet = CompiledStyleSheet(css)

    props = compiled_style_sheet.match(SelectorProperties("mytype"))

    assert props.get("test-font-family") == "sans"
    assert props.get("test-font-size") == 42


def test_empty_compiled_style_sheet():
    css = ""

    compiled_style_sheet = CompiledStyleSheet(css)

    props = compiled_style_sheet.match(SelectorProperties("mytype"))

    assert props == {}
