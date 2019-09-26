import pytest

from gi.repository import GLib, Gio
from gaphor.abc import ActionProvider
from gaphor.action import action, toggle_action, radio_action
from gaphor.services.componentregistry import ComponentRegistry
from gaphor.ui.actiongroup import apply_application_actions, window_action_group


class DummyActionProvider(ActionProvider):
    def __init__(self):
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
def dummy_action_provider():
    return DummyActionProvider()


@pytest.fixture
def component_registry(dummy_action_provider):
    component_registry = ComponentRegistry()
    component_registry.register(dummy_action_provider, "dummy_action_provider")
    return component_registry


def test_window_action_group(component_registry):

    action_group = window_action_group(component_registry)

    assert action_group.lookup_action("new")
    assert not action_group.lookup_action("quit")


def test_application_actions(component_registry):
    action_group = apply_application_actions(
        component_registry, Gio.SimpleActionGroup.new()
    )

    assert not action_group.lookup_action("new")
    assert action_group.lookup_action("quit")


def test_activate_application_action(component_registry, dummy_action_provider):

    action_group = apply_application_actions(
        component_registry, Gio.SimpleActionGroup.new()
    )
    action_group.lookup_action("quit").activate(None)

    assert dummy_action_provider.quit_called


def test_activate_toggle_action(component_registry, dummy_action_provider):
    action_group = window_action_group(component_registry)
    action_group.lookup_action("toggle").change_state(GLib.Variant.new_boolean(True))

    assert dummy_action_provider.toggle_state is True
