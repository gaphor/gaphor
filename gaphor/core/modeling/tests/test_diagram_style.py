import gaphas
import pytest

from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory, Presentation, StyleSheet
from gaphor.core.modeling.diagram import Diagram, StyledDiagram, StyledItem


@pytest.fixture
def event_manager():
    return EventManager()


@pytest.fixture
def element_factory(event_manager):
    return ElementFactory(event_manager)


@pytest.fixture
def diagram(element_factory):
    diagram = element_factory.create(Diagram)
    yield diagram
    diagram.unlink()


class DemoItem(gaphas.Element, Presentation):
    def __init__(self, diagram, id):
        super().__init__(connections=diagram.connections, diagram=diagram, id=id)


def test_name_does_not_have_item_suffix(diagram: Diagram):
    item = diagram.create(DemoItem)
    node = StyledItem(item)

    assert node.name() == "demo"


def test_diagram_is_parent_of_item(diagram: Diagram):
    item = diagram.create(DemoItem)
    node = StyledItem(item)

    assert node.parent().name() == "diagram"


def test_diagram_has_no_parent(diagram):
    node = StyledDiagram(diagram)

    assert node.parent() is None


def test_style_sheet_has_default_style():
    style_sheet = StyleSheet()

    assert "diagram {" in style_sheet.styleSheet
