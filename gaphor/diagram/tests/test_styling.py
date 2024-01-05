from gaphor import UML
from gaphor.core.modeling import StyleSheet
from gaphor.core.modeling.diagram import StyledDiagram
from gaphor.UML.classes import ClassItem


def test_sub_expression(diagram, create, element_factory):
    style_sheet = element_factory.create(StyleSheet)
    style_sheet.styleSheet = ":root:has(class name) { color: blue; }"
    create(ClassItem, UML.Class)

    compiled_style_sheet = style_sheet.new_compiled_style_sheet()
    props = compiled_style_sheet.compute_style(StyledDiagram(diagram))

    assert props["color"] == (0, 0, 1, 1)
