import pytest

from gaphor.ui.toolbox import Toolbox


@pytest.fixture
def toolbox(event_manager, modeling_language):
    return Toolbox(
        event_manager=event_manager, properties={}, modeling_language=modeling_language
    )


def test_toolbox_construction(toolbox):
    widget = toolbox.open()

    assert widget


def test_current_tool(toolbox):
    tool_name = toolbox.active_tool_name

    assert tool_name == "toolbox-pointer"
