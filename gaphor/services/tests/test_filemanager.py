import pytest

from gaphor.application import Application


@pytest.fixture
def application():
    Application.init(
        services=[
            "event_manager",
            "component_registry",
            "file_manager",
            "element_factory",
            "properties",
            "main_window",
            "action_manager",
        ]
    )
    recent_files_backup = Application.get_service("properties").get("recent-files")
    yield Application
    Application.get_service("properties").set("recent-files", recent_files_backup)
    Application.shutdown()
