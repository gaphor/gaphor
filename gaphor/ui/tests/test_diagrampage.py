import pytest
from gaphas.examples import Box

from gaphor.core.modeling import Comment, Diagram
from gaphor.diagram.general.comment import CommentItem
from gaphor.ui.mainwindow import DiagramPage
from gaphor.UML.modelprovider import UMLModelProvider


@pytest.fixture
def page(diagram, event_manager, element_factory, properties):
    page = DiagramPage(
        diagram, event_manager, element_factory, properties, UMLModelProvider()
    )
    page.construct()
    assert page.diagram == diagram
    assert page.view.canvas == diagram.canvas
    yield page
    page.close()


def test_creation(page, element_factory):
    assert len(element_factory.lselect()) == 1


def test_placement(diagram, page, element_factory):
    box = Box()
    diagram.canvas.add(box)
    diagram.canvas.update_now()
    page.view.request_update([box])

    diagram.create(CommentItem, subject=element_factory.create(Comment))
    assert len(element_factory.lselect()) == 2
