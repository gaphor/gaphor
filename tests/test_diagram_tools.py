import pytest

from gaphor.application import Session
from gaphor.core.modeling import Diagram
from gaphor.diagram.event import DiagramOpened


@pytest.fixture
def session():
    session = Session(
        services=[
            "event_manager",
            "component_registry",
            "element_factory",
            "element_dispatcher",
            "modeling_language",
            "sanitizer",
            "main_window",
            "properties",
            "model_browser",
            "diagrams",
            "toolbox",
            "export_menu",
            "tools_menu",
            "elementeditor",
        ]
    )
    session.get_service("main_window").open()
    yield session
    session.shutdown()


@pytest.fixture
def event_manager(session):
    return session.get_service("event_manager")


@pytest.fixture
def component_registry(session):
    return session.get_service("component_registry")


@pytest.fixture
def element_factory(session):
    return session.get_service("element_factory")


@pytest.fixture
def diagram(event_manager, element_factory):
    diagram = element_factory.create(Diagram)
    event_manager.handle(DiagramOpened(diagram))
    return diagram
