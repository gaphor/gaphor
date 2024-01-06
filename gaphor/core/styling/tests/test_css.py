import pytest

from gaphor.core.styling import (
    CompiledStyleSheet,
    compile_style_sheet,
)
from gaphor.core.styling.declarations import WhiteSpace
from gaphor.core.styling.pseudo import compute_pseudo_element_style
from gaphor.core.styling.tests.test_compiler import Node


def first_decl_block(css):
    _, value = next(compile_style_sheet(css))
    return value


def test_empty_css():
    css = ""
    rules = list(compile_style_sheet(css))

    assert not rules


def test_css_content_for_integer():
    css = """
    * {
        font-size: 42;
    }
    """
    props = first_decl_block(css)

    assert props["font-size"] == 42


def test_css_content_for_string():
    css = """
    * {
        font-family: 'sans';
    }
    """
    props = first_decl_block(css)

    assert props["font-family"] == "sans"


def test_css_content_for_ident():
    css = """
    * {
        font-family: sans;
    }
    """
    props = first_decl_block(css)

    assert props["font-family"] == "sans"


def test_css_content_for_tuple():
    css = """
    * {
        padding: 1 2 3 4;
    }
    """
    props = first_decl_block(css)

    assert props["padding"] == (1.0, 2.0, 3.0, 4.0)


def test_multiple_rules():
    css = """
    * {}
    item {}
    """

    rules = list(compile_style_sheet(css))

    assert len(rules) == 2


def test_combined_rules():
    css = """
    foo, bar {}
    """
    rules = list(compile_style_sheet(css))

    assert len(rules) == 2


def test_invalid_css_syntax():
    css = """
    foo/bar ;
    """
    rules = list(compile_style_sheet(css))
    selector, _ = rules[0]

    assert len(rules) == 1
    assert selector == "error"


def test_invalid_css_syntax_in_declarations():
    css = """
    foo { foo : bar : baz }
    """
    rules = list(compile_style_sheet(css))
    _, decls = rules[0]

    assert len(rules) == 1
    assert len(decls) == 0


def test_invalid_selector():
    css = """
    foo/bar {}
    good {}
    """
    rules = list(compile_style_sheet(css))
    selector, _ = rules[0]

    assert len(rules) == 2
    assert selector == "error"


def test_css_declaration_without_semicolon():
    css = """
    * {
        font-family: 'sans'
    }
    """
    props = first_decl_block(css)

    assert props.get("font-family") == "sans"


def test_css_multiple_declarations_without_semicolons():
    css = """
    * {
        font-family: sans;
        font-size: 42
    }
    """
    props = first_decl_block(css)

    assert props.get("font-family") == "sans"
    assert props.get("font-size") == 42


def test_compiled_style_sheet():
    css = """
    * {
        font-size: 42;
        font-family: overridden
    }
    mytype {
        font-family: sans
    }
    """

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("mytype"))

    assert props.get("font-family") == "sans"
    assert props.get("font-size") == 42


@pytest.mark.parametrize(
    "font_size", ["x-small", "small", "medium", "large", "x-large"]
)
def test_relative_font_size(font_size):
    css = f"* {{ font-size: {font_size} }}"

    props = first_decl_block(css)
    assert props.get("font-size") == font_size


@pytest.mark.parametrize("font_size", ["foo", "xx-small", "xx-large"])
def test_faulty_font_size(font_size):
    css = f"* {{ font-size: {font_size} }}"

    props = first_decl_block(css)
    assert props.get("font-size") is None


def filter_private(props):
    return {n: v for n, v in props.items() if not n.startswith("-gaphor-")}


def test_empty_compiled_style_sheet():
    css = ""

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("mytype"))

    assert filter_private(props) == {}


def test_color():
    css = "mytype { color: #00ff00 }"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("mytype"))

    assert props.get("color") == (0, 1, 0, 1)


def test_color_typing_in_progress():
    css = "mytype { color: # }"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("mytype"))

    assert props.get("color") is None


@pytest.mark.parametrize(
    "css_value,result",
    [
        ["normal", 0.0],
        ["sloppy", 0.5],
        ["sloppy 0.3", 0.3],
        ["sloppy -0.1", -0.1],
        ["sloppy 2.1", 2.0],
        ["sloppy -2.1", -2.0],
        ["sloppy wrong", 0.5],
    ],
)
def test_line_style(css_value, result):
    css = f"mytype {{ line-style: {css_value} }}"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("mytype"))

    assert props.get("line-style") == result


@pytest.mark.parametrize(
    "css_value,result",
    [
        [0.5, 0.5],
        [0, 0.0],
        [1, 1.0],
        [-0.1, None],
        [1.1, None],
        ["wrong", None],
    ],
)
def test_opacity(css_value, result):
    css = f"mytype {{ opacity: {css_value} }}"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("mytype"))

    assert props.get("opacity") == result


def test_broken_line_style():
    # diagram css is missing the closing bracket
    css = "diagram { line-style: sloppy * { }"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("mytype"))

    assert props.get("line-style") is None


def test_variable():
    css = "diagram { --myvar: 12; line-width: var(--myvar) }"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("diagram"))

    assert props.get("line-width") == 12


def test_variable_color():
    css = "* { --mycolor: #123456 } diagram { color: var(--mycolor) }"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("diagram"))

    assert props.get("color") == pytest.approx(
        (0x12 / 255.0, 0x34 / 255.0, 0x56 / 255.0, 1.0)
    )


def test_unknown_variable():
    css = "diagram { line-width: var(--myvar) }"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("diagram"))

    assert props.get("line-width") is None


def test_unknown_variable_should_use_original_value():
    css = "* { line-width: 1.0 } diagram { line-width: var(--myvar) }"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("diagram"))

    assert props.get("line-width") == pytest.approx(1.0)


def test_unknown_variable_resolve_original_value():
    css = "* { line-width: var(--lw); --lw: 1.0 } diagram { line-width: var(--myvar) }"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("diagram"))

    assert props.get("line-width") == pytest.approx(1.0)


def test_variable_cannot_contain_a_variable():
    css = "* { line-width: var(--a); --a: var(--b); --b: 1.0 }"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("diagram"))

    assert props.get("line-width") is None


def test_variable_with_property():
    css = "* { line-width: var(line-width); }"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("diagram"))

    assert props.get("line-width") is None


def test_color_schemes():
    css = """
        * { line-width: 1; }
        @media dark-mode {
         * { line-width: 2; }
        }
        @media light-mode {
         * { line-width: 3; }
        }
    """

    compiled_style_sheet = CompiledStyleSheet(css)
    normal_props = compiled_style_sheet.compute_style(Node("node"))
    dark_props = compiled_style_sheet.compute_style(Node("node", dark_mode=True))
    light_props = compiled_style_sheet.compute_style(Node("node", dark_mode=False))

    assert normal_props.get("line-width") == pytest.approx(1.0)
    assert dark_props.get("line-width") == pytest.approx(2.0)
    assert light_props.get("line-width") == pytest.approx(3.0)


@pytest.mark.parametrize(
    "white_space_value,result",
    [
        ["normal", WhiteSpace.NORMAL],
        ["nowrap", WhiteSpace.NOWRAP],
        ["none", None],
    ],
)
def test_white_space_normal(white_space_value, result):
    css = f"* {{ white-space: {white_space_value} }}"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("node"))

    assert props.get("white-space") is result


def test_pseudo_element():
    css = "class::after { content: 'Hi' }"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("class", pseudo="after"))

    assert props.get("content") == "Hi"


def test_bare_pseudo_element():
    css = "::after { content: 'Hi' }"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("node", pseudo="after"))

    assert props.get("content") == "Hi"


def test_combined_normal_and_pseudo_element():
    css = "node, class::after { content: 'Hi' }"

    compiled_style_sheet = CompiledStyleSheet(css)
    node_props = compiled_style_sheet.compute_style(Node("node"))
    class_props = compiled_style_sheet.compute_style(Node("class", pseudo="after"))

    assert node_props.get("content") == "Hi"
    assert class_props.get("content") == "Hi"


def test_pseudo_element_inherits_normal_declarations():
    css = "node { color: blue} ::after { content: 'Hi' }"

    compiled_style_sheet = CompiledStyleSheet(css)
    props = compiled_style_sheet.compute_style(Node("node"))
    after = compute_pseudo_element_style(props, "after")

    assert after
    assert after.get("content") == "Hi"
