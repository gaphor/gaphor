import pytest

from gaphor.core.modeling import Comment, Diagram, StyleSheet
from gaphor.diagram.general import Box
from gaphor.diagram.general.comment import CommentItem
from gaphor.ui.diagrampage import DiagramPage, placement_icon_base
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


@pytest.mark.skip(reason="This test cases a Segmentation Fault when run from VSCode")
def test_placement_icon_base_is_loaded_once():
    icon1 = placement_icon_base()
    icon2 = placement_icon_base()

    assert icon1 is icon2
