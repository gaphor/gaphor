import pytest

from gaphor import UML
from gaphor.application import Application
from gaphor.ui.event import DiagramOpened
from gaphor.ui.abc import UIComponent


@pytest.fixture
def application():
    Application.init(
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
    yield Application
    Application.shutdown()


def get_current_diagram(app):
    return app.component_registry.get(UIComponent, "diagrams").get_current_diagram()


def test_creation(application):
    # MainWindow should be created as resource
    main_w = application.get_service("main_window")
    main_w.open()
    assert get_current_diagram(application) is None


def test_show_diagram(application):
    element_factory = application.get_service("element_factory")
    diagram = element_factory.create(UML.Diagram)
    main_w = application.get_service("main_window")
    main_w.open()
    event_manager = application.get_service("event_manager")
    event_manager.handle(DiagramOpened(diagram))
    assert get_current_diagram(application) == diagram
