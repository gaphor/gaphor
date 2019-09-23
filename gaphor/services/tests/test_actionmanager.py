import pytest

from gi.repository import GLib, Gio
from gaphor.abc import ActionProvider
from gaphor.action import action, toggle_action, radio_action, build_action_group
from gaphor.services.actionmanager import ActionManager
from gaphor.services.componentregistry import ComponentRegistry
from gaphor.services.eventmanager import EventManager
from gaphor.services.filemanager import FileManager
from gaphor.services.properties import Properties
from gaphor.application import Application


class DummyActionProvider(ActionProvider):

    menu_xml = "<ui></ui>"

    def __init__(self):
        self.action_group = build_action_group(self)
        self.quit_called = False
        self.toggle_state = None

    @action(name="app.quit")
    def quit(self):
        self.quit_called = True

    @action(name="new")
    def new(self):
        pass

    @toggle_action(name="toggle")
    def toggle(self, state):
        print("State", state)
        self.toggle_state = state

    # @radio_action(names=["radio1", "radio2"])
    # def radio(self, state):
    #     self.radio_state = state


@pytest.fixture
def event_manager():
    return EventManager()


@pytest.fixture
def component_registry():
    return ComponentRegistry()


@pytest.fixture
def action_manager(event_manager, component_registry):
    action_manager = ActionManager(event_manager, component_registry)
    return action_manager


@pytest.fixture
def file_manager(event_manager):
    properties = Properties(event_manager)
    return FileManager(event_manager, None, None, properties)


def test_load_all_menus(action_manager, file_manager):
    action_manager.register_action_provider(file_manager)

    ui = action_manager.ui_manager.get_ui()

    assert '<menuitem name="quit" action="quit"/>' in ui, ui
    assert '<menuitem name="file-new" action="file-new"/>' in ui, ui


def test_window_action_group(action_manager):
    dummy = DummyActionProvider()
    action_manager.register_action_provider(dummy)

    action_group = action_manager.window_action_group()

    assert action_group.lookup("new")
    assert not action_group.lookup("quit")


def test_application_actions(action_manager):
    dummy = DummyActionProvider()
    action_manager.register_action_provider(dummy)

    action_group = action_manager.apply_application_actions(Gio.SimpleActionGroup.new())

    assert not action_group.lookup("new")
    assert action_group.lookup("quit")


def test_activate_application_action(action_manager):
    dummy = DummyActionProvider()
    action_manager.register_action_provider(dummy)

    action_group = action_manager.apply_application_actions(Gio.SimpleActionGroup.new())
    action_group.lookup("quit").activate(None)

    assert dummy.quit_called


def test_activate_toggle_action(action_manager):
    dummy = DummyActionProvider()
    action_manager.register_action_provider(dummy)

    action_group = action_manager.window_action_group()
    action_group.lookup("toggle").activate(GLib.Variant.new_boolean(True))

    assert dummy.toggle_state is True
