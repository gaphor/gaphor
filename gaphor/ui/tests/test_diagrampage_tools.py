import pytest
from gi.repository import Gtk

from gaphor import UML
from gaphor.diagram.diagramtoolbox_actions import toolbox_actions
from gaphor.services.eventmanager import EventManager
from gaphor.services.properties import Properties
from gaphor.ui.diagrampage import DiagramPage
from gaphor.UML import ElementFactory


@pytest.fixture
def event_manager():
    return EventManager()


@pytest.fixture
def element_factory(event_manager):
    return ElementFactory(event_manager)


@pytest.fixture
def properties(event_manager):
    return Properties(event_manager)


@pytest.fixture
def tab(event_manager, element_factory, properties):
    diagram = element_factory.create(UML.Diagram)
    tab = DiagramPage(diagram, event_manager, element_factory, properties,)

    window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
    window.add(tab.construct())
    window.show()
    yield tab
    window.destroy()


def get_tool(tab, tool_name, profile=None):
    tool = tab.get_tool(tool_name, profile)
    # Ensure the factory is working
    tool.create_item((0, 0))
    tab.diagram.canvas.update()
    assert tool
    return tool


def test_pointer(tab):
    tool = get_tool(tab, "toolbox-pointer")


@pytest.mark.parametrize(
    "tool_name",
    [
        "toolbox-comment",
        "toolbox-comment-line",
        # Classes:
        "toolbox-class",
        "toolbox-interface",
        "toolbox-package",
        "toolbox-association",
        "toolbox-dependency",
        "toolbox-generalization",
        "toolbox-implementation",
        # Components:
        "toolbox-component",
        "toolbox-node",
        "toolbox-artifact",
        # Actions:
        "toolbox-action",
        "toolbox-initial-node",
        "toolbox-activity-final-node",
        "toolbox-flow-final-node",
        "toolbox-decision-node",
        "toolbox-fork-node",
        "toolbox-flow",
        # Use cases:
        "toolbox-use-case",
        "toolbox-actor",
        "toolbox-use-case-association",
        "toolbox-include",
        "toolbox-extend",
        # Profiles:
        "toolbox-profile",
        "toolbox-metaclass",
        "toolbox-stereotype",
        "toolbox-extension",
    ],
)
def test_placement_action(tab, tool_name):
    get_tool(tab, tool_name, "UML")


def test_placement_object_node(tab, element_factory):
    get_tool(tab, "toolbox-object-node", "UML")
    assert 1 == len(element_factory.lselect(lambda e: isinstance(e, UML.ObjectNode)))


def test_placement_partition(tab, element_factory):
    get_tool(tab, "toolbox-partition", "UML")
    assert 0 == len(
        element_factory.lselect(lambda e: isinstance(e, UML.ActivityPartition))
    )


@pytest.mark.parametrize("profile", ["UML", "SysML", "Safety"])
def test_toolbox_actions_shortcut_unique(profile):

    shortcuts = {}

    for category, items in toolbox_actions(profile):
        for action_name, label, icon_name, shortcut, *rest in items:
            try:
                shortcuts[shortcut].append(action_name)
            except KeyError:
                shortcuts[shortcut] = [action_name]

    for key, val in list(shortcuts.items()):
        if key is not None:
            assert len(val) == 1, f"Duplicate toolbox shortcut {key} for {val}"
