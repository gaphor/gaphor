import pytest
from gaphor.application import Application
from gaphor.services.diagramexportmanager import DiagramExportManager


@pytest.fixture
def application():
    Application.init(
        services=[
            "event_manager",
            "component_registry",
            "properties",
            "diagram_export_manager",
        ]
    )
    yield Application
    Application.shutdown()


def test_init_from_application(application):
    application.get_service("diagram_export_manager")
