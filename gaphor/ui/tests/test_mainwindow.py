import pytest

from gaphor import UML
from gaphor.application import Application
from gaphor.ui.abc import UIComponent
from gaphor.ui.event import DiagramOpened


@pytest.fixture
def session():
    session = Application.new_session(
        services=[
            "event_manager",
            "component_registry",
            "element_factory",
            "properties",
            "main_window",
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


def get_current_diagram(session):
    return (
        session.get_service("component_registry")
        .get(UIComponent, "diagrams")
        .get_current_diagram()
    )


def test_creation(session):
    # MainWindow should be created as resource
    main_w = session.get_service("main_window")
    main_w.open()
    assert get_current_diagram(session) is None


def test_show_diagram(session):
    element_factory = session.get_service("element_factory")
    diagram = element_factory.create(UML.Diagram)
    main_w = session.get_service("main_window")
    main_w.open()
    event_manager = session.get_service("event_manager")
    event_manager.handle(DiagramOpened(diagram))
    assert get_current_diagram(session) == diagram
