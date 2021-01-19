import pytest

from gaphor.application import Session
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram
from gaphor.diagram.diagramtools import new_item_factory
from gaphor.diagram.diagramtools.placement import (
    PlacementState,
    on_drag_begin,
    on_drag_end,
    placement_tool,
)
from gaphor.diagram.general import CommentLineItem
from gaphor.ui.appfilemanager import load_default_model
from gaphor.ui.diagrampage import DiagramPage
from gaphor.UML.modelinglanguage import UMLModelingLanguage


@pytest.fixture
def session():
    session = Session()
    load_default_model(session)
    yield session
    session.shutdown()


@pytest.fixture
def event_manager(session):
    return session.get_service("event_manager")


@pytest.fixture
def element_factory(session):
    return session.get_service("element_factory")


@pytest.fixture
def diagram(element_factory, event_manager):
    with Transaction(event_manager):
        return element_factory.create(Diagram)


@pytest.fixture
def view(diagram, event_manager, element_factory):
    page = DiagramPage(
        diagram, event_manager, element_factory, {}, UMLModelingLanguage()
    )
    page.construct()
    return page.view


def click(tool, event_manager):
    factory = new_item_factory(CommentLineItem)
    state = PlacementState(factory, event_manager, handle_index=-1)
    on_drag_begin(tool, 0, 0, state)
    on_drag_end(tool, 0, 0, state)


def test_placement(view, event_manager):
    factory = new_item_factory(CommentLineItem)
    tool = placement_tool(view, factory, event_manager, handle_index=-1)

    with Transaction(event_manager):
        click(tool, event_manager)
        click(tool, event_manager)
