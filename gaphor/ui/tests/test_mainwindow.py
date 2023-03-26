import pytest

from gaphor.application import Session
from gaphor.core.modeling import Comment, Diagram
from gaphor.diagram.event import DiagramOpened
from gaphor.ui.abc import UIComponent
from gaphor.ui.event import ElementOpened


@pytest.fixture
def session():
    session = Session(
        services=[
            "event_manager",
            "component_registry",
            "element_factory",
            "modeling_language",
            "properties",
            "main_window",
            "model_browser",
            "diagrams",
            "toolbox",
            "elementeditor",
            "export_menu",
            "tools_menu",
        ]
    )
    main_w = session.get_service("main_window")
    main_w.open()
    yield session
    session.shutdown()


def get_current_diagram(session):
    return (
        session.get_service("component_registry")
        .get(UIComponent, "diagrams")
        .get_current_diagram()
    )


def test_creation(session):
    assert get_current_diagram(session) is None


def test_show_diagram(session):
    element_factory = session.get_service("element_factory")
    diagram = element_factory.create(Diagram)

    event_manager = session.get_service("event_manager")
    event_manager.handle(DiagramOpened(diagram))
    assert get_current_diagram(session) == diagram


def test_close_diagram(session):
    element_factory = session.get_service("element_factory")
    diagram = element_factory.create(Diagram)

    event_manager = session.get_service("event_manager")
    event_manager.handle(DiagramOpened(diagram))

    diagrams = session.get_service("diagrams")
    diagrams.close_current_tab()

    assert not get_current_diagram(session)


def test_open_element_on_diagram(session):
    element_factory = session.get_service("element_factory")
    diagram = element_factory.create(Diagram)
    comment = element_factory.create(Comment)

    event_manager = session.get_service("event_manager")
    event_manager.handle(DiagramOpened(diagram))

    event_manager.handle(ElementOpened(comment))

    assert comment.presentation
    assert comment.presentation[0] in get_current_diagram(session).ownedPresentation


def test_update_diagram_name(session):
    element_factory = session.get_service("element_factory")
    diagram = element_factory.create(Diagram)

    event_manager = session.get_service("event_manager")
    event_manager.handle(DiagramOpened(diagram))

    diagram.name = "Foo"


def test_flush_model(session):
    element_factory = session.get_service("element_factory")
    diagram = element_factory.create(Diagram)

    event_manager = session.get_service("event_manager")
    event_manager.handle(DiagramOpened(diagram))

    element_factory.flush()
