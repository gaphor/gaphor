import cssselect2
import pytest
import tinycss2

from gaphor.core.styling import StyleDeclarations, parse_stylesheet


def first_decl_block(css):
    _, value = next(parse_stylesheet(css))
    return value


@StyleDeclarations.register("test-padding", "test-font-size", "test-font-family")
def dummy_style_declaration(prop, value):
    return value


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

    rules = list(parse_stylesheet(css))

    assert len(rules) == 2


def test_selectors():
    css = """
    foo, bar {}
    """
    selector, declarations = next(parse_stylesheet(css))

    assert len(selector) == 2


def test_invalid_css_syntax():
    css = """
    foo/bar ;
    """
    rules = list(parse_stylesheet(css))
    selector, _ = rules[0]

    assert len(rules) == 1
    assert selector == "error"


def test_invalid_css_syntax_in_declarations():
    css = """
    foo { foo : bar : baz }
    """
    rules = list(parse_stylesheet(css))
    _, decls = rules[0]

    assert len(rules) == 1
    assert len(decls) == 0


def test_invalid_selector():
    css = """
    foo/bar {}
    good {}
    """
    rules = list(parse_stylesheet(css))
    selector, _ = rules[0]

    assert len(rules) == 2
    assert selector == "error"
