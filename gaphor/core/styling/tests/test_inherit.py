from gaphor.core.styling import CompiledStyleSheet
from gaphor.core.styling.inherit import compute_inherited_style
from gaphor.core.styling.tests.test_compiler import Node
from gaphor.diagram.shapes import Box, CssNode


def test_inherit_from_parent_style():
    css = "node { font-size: 10 } node sub { content: 'Hi' }"

    compiled_style_sheet = CompiledStyleSheet(css)
    style = compiled_style_sheet.compute_style(Node("node"))
    inherited = compute_inherited_style(
        style, CssNode("sub", None, Box()).style_node(style)
    )

    assert inherited.get("font-size") == 10
    assert inherited.get("content") == "Hi"


def test_should_not_inherit_everything():
    css = """
    node { background-color: blue }
    node sub { content: 'Hi' }
    node sub * { font-size: 10 }
    """

    compiled_style_sheet = CompiledStyleSheet(css)
    style = compiled_style_sheet.compute_style(Node("node"))
    inherited = compute_inherited_style(
        style,
        CssNode("sub", None, Box()).style_node(
            compute_inherited_style(
                style, CssNode("sub", None, Box()).style_node(style)
            )
        ),
    )

    assert not inherited.get("background-color")
    assert inherited.get("content") == "Hi"
    assert inherited.get("font-size") == 10
