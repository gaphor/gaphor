import pytest
from gaphas.examples import Box

from gaphor import UML
from gaphor.application import Session
from gaphor.diagram.general.comment import CommentItem
from gaphor.ui.mainwindow import DiagramPage


@pytest.fixture
def session():
    session = Session(
        services=[
            "event_manager",
            "component_registry",
            "element_factory",
            "main_window",
            "properties",
            "namespace",
            "diagrams",
            "toolbox",
            "elementeditor",
            "export_menu",
            "tools_menu",
        ]
    )
    yield session
    session.shutdown()


@pytest.fixture
def main_window(session):
    main_window = session.get_service("main_window")
    main_window.open()


@pytest.fixture
def element_factory(session):
    return session.get_service("element_factory")


@pytest.fixture
def diagram(element_factory):
    diagram = element_factory.create(UML.Diagram)
    yield diagram
    diagram.unlink()


@pytest.fixture
def page(session, diagram, element_factory):
    page = DiagramPage(
        diagram,
        session.get_service("event_manager"),
        element_factory,
        session.get_service("properties"),
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

    diagram.create(CommentItem, subject=element_factory.create(UML.Comment))
    assert len(element_factory.lselect()) == 2
