import cssselect2
import pytest
import tinycss2

from gaphor.core.styling import StyleDeclarations, parse_stylesheet


@StyleDeclarations.register("test-padding", "test-font-size", "test-font-family")
def dummy_style_declaration(prop, value):
    return value


def test_css_content_for_integer():
    css = """
    * {
        test-font-size: 42;
    }
    """
    props = parse_stylesheet(css)

    assert props["test-font-size"] == 42


def test_css_content_for_string():
    css = """
    * {
        test-font-family: 'sans';
    }
    """
    props = parse_stylesheet(css)

    assert props["test-font-family"] == "sans"


def test_css_content_for_ident():
    css = """
    * {
        test-font-family: sans;
    }
    """
    props = parse_stylesheet(css)

    assert props["test-font-family"] == "sans"


def test_css_content_for_tuple():
    css = """
    * {
        test-padding: 1 2 3 4;
    }
    """
    props = parse_stylesheet(css)

    assert props["test-padding"] == (1.0, 2.0, 3.0, 4.0)
