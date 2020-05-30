import pytest
from gaphas.item import Item

from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling.diagram import Diagram
from gaphor.core.modeling.elementfactory import ElementFactory
from gaphor.core.modeling.presentation import Presentation, StyleSheet


class StubItem(Presentation, Item):
    pass


@pytest.fixture
def element_factory():
    event_manager = EventManager()
    return ElementFactory(event_manager)


@pytest.fixture
def diagram(element_factory):
    return element_factory.create(Diagram)


def test_presentation_stylesheet(diagram, element_factory):
    styleSheet = element_factory.create(StyleSheet)
    presentation = diagram.create(StubItem)

    assert presentation.styleSheet is styleSheet


def test_presentation_stylesheet_is_absent(diagram):
    presentation = diagram.create(StubItem)

    assert presentation.styleSheet is None
