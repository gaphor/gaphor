from typing import Dict, List

import pytest
from gi.repository import Gtk

from gaphor import UML
from gaphor.C4Model.toolbox import c4model_toolbox_actions
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import Diagram
from gaphor.core.modeling.elementfactory import ElementFactory
from gaphor.diagram.diagramtoolbox import get_tool_def
from gaphor.diagram.tools.placement import PlacementState, on_drag_begin
from gaphor.RAAML.toolbox import raaml_toolbox_actions
from gaphor.SysML.toolbox import sysml_toolbox_actions
from gaphor.ui.diagrampage import DiagramPage
from gaphor.UML.modelinglanguage import UMLModelingLanguage
from gaphor.UML.toolbox import uml_toolbox_actions


@pytest.fixture
def event_manager():
    return EventManager()


@pytest.fixture
def element_factory(event_manager):
    element_factory = ElementFactory(event_manager)
    yield element_factory
    element_factory.shutdown()


@pytest.fixture
def properties():
    return {}


@pytest.fixture
def tab(event_manager, element_factory):
    diagram = element_factory.create(Diagram)
    tab = DiagramPage(diagram, event_manager, UMLModelingLanguage())

    window = Gtk.Window.new()
    window.set_child(tab.construct())

    window.set_visible(True)
    yield tab
    window.destroy()


def test_pointer(tab):
    tab.apply_tool_set("toolbox-pointer")

    # TODO: what's the observed behavior?
    assert tab.view._controllers  # noqa: SLF001


def flatten(list):
    return [item for sublist in list for item in sublist]


@pytest.mark.parametrize(
    "tool_def",
    set(
        flatten(
            [
                flatten(section.tools for section in uml_toolbox_actions),
                flatten(section.tools for section in sysml_toolbox_actions),
                flatten(section.tools for section in raaml_toolbox_actions),
                flatten(section.tools for section in c4model_toolbox_actions),
            ]
        )
    ),
)
def test_placement_action(tool_def, tab, event_manager):
    if not tool_def.item_factory:
        return

    tool = Gtk.GestureDrag.new()
    tab.view.add_controller(tool)

    placement_state = PlacementState(
        tool_def.item_factory, event_manager, tool_def.handle_index
    )
    on_drag_begin(tool, 0, 0, placement_state)
    tab.view.update()


def test_placement_object_node(tab, element_factory, event_manager):
    test_placement_action(
        get_tool_def(UMLModelingLanguage(), "toolbox-object-node"), tab, event_manager
    )
    assert len(element_factory.lselect(UML.ObjectNode)) == 1


def test_placement_partition(tab, element_factory, event_manager):
    test_placement_action(
        get_tool_def(UMLModelingLanguage(), "toolbox-partition"), tab, event_manager
    )

    assert len(element_factory.lselect(UML.ActivityPartition)) == 2


@pytest.mark.parametrize(
    "toolbox_actions",
    [
        uml_toolbox_actions,
        sysml_toolbox_actions,
        raaml_toolbox_actions,
        c4model_toolbox_actions,
    ],
)
def test_uml_toolbox_actions_shortcut_unique(toolbox_actions):
    shortcuts: Dict[str, List[str]] = {}

    for _category, items in toolbox_actions:
        for action_name, _label, _icon_name, shortcut, *_rest in items:
            try:
                shortcuts[shortcut].append(action_name)
            except KeyError:
                shortcuts[shortcut] = [action_name]

    for key, val in list(shortcuts.items()):
        if key is not None:
            assert len(val) == 1, f"Duplicate toolbox shortcut {key} for {val}"
