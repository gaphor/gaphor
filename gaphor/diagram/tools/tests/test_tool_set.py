from gaphas.tool.rubberband import RubberbandState

from gaphor.diagram.diagramtoolbox import new_item_factory
from gaphor.diagram.general import Box
from gaphor.diagram.tools import (
    apply_default_tool_set,
    apply_magnet_tool_set,
    apply_placement_tool_set,
)


def test_default_tool_set(view, modeling_language, event_manager):
    apply_default_tool_set(view, modeling_language, event_manager, RubberbandState())

    assert view.observe_controllers()


def test_magnet_tool_set(view, modeling_language, event_manager):
    apply_magnet_tool_set(view, modeling_language, event_manager)

    assert view.observe_controllers()


def test_placement_tool_set(view, modeling_language, event_manager):
    apply_placement_tool_set(
        view, new_item_factory(Box), modeling_language, event_manager, 0
    )

    assert view.observe_controllers()
