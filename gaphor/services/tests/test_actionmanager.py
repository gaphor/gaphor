import pytest

from gi.repository import Gio
from gaphor.services.actionmanager import ActionManager
from gaphor.services.componentregistry import ComponentRegistry
from gaphor.services.eventmanager import EventManager
from gaphor.services.filemanager import FileManager
from gaphor.services.properties import Properties
from gaphor.application import Application


@pytest.fixture
def event_manager():
    return EventManager()


@pytest.fixture
def component_registry():
    return ComponentRegistry()


@pytest.fixture
def action_manager(event_manager, component_registry):
    return ActionManager(event_manager, component_registry)


@pytest.fixture
def file_manager(event_manager):
    properties = Properties(event_manager)
    return FileManager(event_manager, None, None, properties)


def test_load_all_menus(action_manager, file_manager):
    action_manager.register_action_provider(file_manager)

    ui = action_manager.ui_manager.get_ui()

    assert '<menuitem name="quit" action="quit"/>' in ui, ui
    assert '<menuitem name="file-new" action="file-new"/>' in ui, ui


def test_window_action_group(action_manager, file_manager):
    action_manager.register_action_provider(file_manager)

    action_group = action_manager.window_action_group()

    assert action_group.lookup("file-new")
    assert not action_group.lookup("quit")

    
def test_application_actions(action_manager, file_manager):
    action_manager.register_action_provider(file_manager)

    action_group = action_manager.apply_application_actions(Gio.SimpleActionGroup.new())

    assert not action_group.lookup("file-new")
    assert action_group.lookup("quit")
