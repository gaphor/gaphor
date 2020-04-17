import pytest
from gi.repository import Gio, GLib

from gaphor.abc import ActionProvider
from gaphor.action import action
from gaphor.services.componentregistry import ComponentRegistry
from gaphor.ui.actiongroup import (
    apply_application_actions,
    as_variant_type,
    from_variant,
    to_variant,
    window_action_group,
)


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

    @action(name="toggle", state=True)
    def toggle(self, state):
        self.toggle_state = state

    def dyn_state(self):
        return "my-state"

    @action(name="my-action", state=dyn_state)
    def my_state(self, state):
        pass


@pytest.fixture
def dummy_action_provider():
    return DummyActionProvider()


@pytest.fixture
def component_registry(dummy_action_provider):
    component_registry = ComponentRegistry()
    component_registry.register("dummy_action_provider", dummy_action_provider)
    return component_registry


def test_window_action_group(component_registry):
    action_group, accel_group = window_action_group(component_registry)

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
    action_group, accel_group = window_action_group(component_registry)
    action_group.lookup_action("toggle").change_state(GLib.Variant.new_boolean(True))

    assert dummy_action_provider.toggle_state is True


def test_variant_type_conversion():
    assert as_variant_type(None) is None
    assert as_variant_type(str).equal(GLib.VariantType.new("s"))
    assert as_variant_type(int).equal(GLib.VariantType.new("i"))
    assert as_variant_type(bool).equal(GLib.VariantType.new("b"))


def test_invalid_type_to_variant_type():
    with pytest.raises(ValueError):
        as_variant_type(float)


def test_python_to_variant():
    assert to_variant(None) is None
    assert to_variant("text") == GLib.Variant.new_string("text")
    assert to_variant(123) == GLib.Variant.new_int32(123)
    assert to_variant(True) == GLib.Variant.new_boolean(True)
    assert to_variant(False) == GLib.Variant.new_boolean(False)


def test_invalid_python_to_variant():
    with pytest.raises(ValueError):
        to_variant(1.0)


def test_from_variant_to_python_value():
    assert from_variant(None) is None
    assert from_variant(GLib.Variant.new_string("text")) == "text"
    assert from_variant(GLib.Variant.new_int32(123)) == 123
    assert from_variant(GLib.Variant.new_boolean(True)) is True


def test_invalid_gvariant_to_python():
    with pytest.raises(ValueError):
        from_variant(GLib.Variant.new_double(1.0))


def test_dynamic_state(component_registry):
    action_group, accel_group = window_action_group(component_registry)

    assert action_group.lookup_action("my-action")
    assert (
        from_variant(action_group.lookup_action("my-action").get_state()) == "my-state"
    )
