import pytest

from gaphor.application import Application


@pytest.fixture
def application(
    services=[
        "event_manager",
        "component_registry",
        "file_manager",
        "element_factory",
        "properties",
        "main_window",
        "action_manager",
    ]
):
    Application.init(services=services)
    recent_files_backup = Application.get_service("properties").get("recent-files")
    yield Application
    Application.get_service("properties").set("recent-files", recent_files_backup)
    Application.shutdown()


def test_recent_files(application):
    fileman = application.get_service("file_manager")
    properties = application.get_service("properties")

    # ensure the recent_files list is empty:
    properties.set("recent-files", [])
    fileman.update_recent_files()
    for i in range(0, 9):
        a = fileman.action_group.get_action("file-recent-%d" % i)
        assert a
        assert a.get_property("visible") == False, "%s, %d" % (
            a.get_property("visible"),
            i,
        )

    fileman.filename = "firstfile"
    a = fileman.action_group.get_action("file-recent-%d" % 0)
    assert a
    assert a.get_property("visible") == True
    assert a.props.label == "_1. firstfile", a.props.label
    for i in range(1, 9):
        a = fileman.action_group.get_action("file-recent-%d" % i)
        assert a
        assert a.get_property("visible") == False
