import pytest

from gaphor.application import Session
from gaphor.core.modeling import Comment, Diagram
from gaphor.diagram.event import DiagramOpened
from gaphor.ui.abc import UIComponent
from gaphor.ui.event import ElementOpened
from gaphor.ui.tests.fixtures import iterate_until


@pytest.fixture
def session():
    session = Session(
        services=[
            "diagrams",
            "element_editor",
            "event_manager",
            "export_menu",
            "component_registry",
            "element_factory",
            "main_window",
            "model_browser",
            "model_changed",
            "modeling_language",
            "properties",
            "toolbox",
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


@pytest.mark.skip(reason="May cause funky window manager behavior")
def test_window_mode_maximized(session):
    main_window = session.get_service("main_window")
    properties = session.get_service("properties")

    main_window.window.unfullscreen()
    main_window.window.maximize()
    iterate_until(lambda: properties.get("ui.window-mode") == "maximized")

    assert properties.get("ui.window-mode") == "maximized"

    main_window.window.unmaximize()


@pytest.mark.skip(reason="May cause funky window manager behavior")
def test_window_mode_fullscreened(session):
    main_window = session.get_service("main_window")
    properties = session.get_service("properties")

    main_window.window.fullscreen()
    iterate_until(lambda: properties.get("ui.window-mode") == "fullscreened")

    assert properties.get("ui.window-mode") == "fullscreened"

    main_window.window.unfullscreen()


def test_window_mode_normal(session):
    main_window = session.get_service("main_window")
    properties = session.get_service("properties")

    main_window.window.unfullscreen()
    main_window.window.unmaximize()
    iterate_until(lambda: properties.get("ui.window-mode") == "")

    assert properties.get("ui.window-mode") == ""
