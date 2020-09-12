import pytest

from gaphor.core.modeling import Comment, Diagram, StyleSheet
from gaphor.diagram.general import Box
from gaphor.diagram.general.comment import CommentItem
from gaphor.ui.diagrams import DiagramPage
from gaphor.UML.modelinglanguage import UMLModelingLanguage


@pytest.fixture
def page(diagram, event_manager, element_factory, properties):
    page = DiagramPage(
        diagram, event_manager, element_factory, properties, UMLModelingLanguage()
    )
    page.construct()
    assert page.diagram == diagram
    assert page.view.canvas == diagram.canvas
    yield page
    page.close()


def test_creation(page, element_factory):
    assert len(element_factory.lselect()) == 2
    assert len(element_factory.lselect(Diagram)) == 1
    assert len(element_factory.lselect(StyleSheet)) == 1


def test_placement(diagram, page, element_factory):
    box = diagram.create(Box)
    page.view.request_update([box])

    diagram.create(CommentItem, subject=element_factory.create(Comment))
    assert len(element_factory.lselect()) == 3
