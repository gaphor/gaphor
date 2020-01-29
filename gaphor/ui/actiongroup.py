from typing import NamedTuple

import gi

from gaphor.abc import ActionProvider

# fmt: off
gi.require_version("Gtk", "3.0")  # noqa: isort:skip
from gi.repository import Gio, GLib, Gtk  # noqa: isort:skip
# fmt: on


class ActionGroup(NamedTuple):
    actions: Gio.SimpleActionGroup
    shortcuts: Gtk.AccelGroup


def apply_application_actions(component_registry, gtk_app):
    scope = "app"
    for _name, provider in component_registry.all(ActionProvider):
        for attrname, act in iter_actions(provider, scope):
            a = create_gio_action(act, provider, attrname)
            gtk_app.add_action(a)
            if act.shortcut:
                gtk_app.add_accelerator(act.shortcut, f"{scope}.{act.name}", None)
    return gtk_app


def window_action_group(component_registry):
    scope = "win"
    action_group = Gio.SimpleActionGroup.new()
    accel_group = Gtk.AccelGroup.new()

    for _name, provider in component_registry.all(ActionProvider):
        create_action_group(
            provider, scope, action_group=action_group, accel_group=accel_group
        )

    return ActionGroup(actions=action_group, shortcuts=accel_group)


def _accel_handler(scope, name):
    return (
        lambda agrp, win, key, mod: win.get_action_group(scope)
        .lookup_action(name)
        .activate()
    )


def create_action_group(provider, scope, action_group=None, accel_group=None):
    if not action_group:
        action_group = Gio.SimpleActionGroup.new()
    if not accel_group:
        accel_group = Gtk.AccelGroup.new()

    for attrname, act in iter_actions(provider, scope):
        a = create_gio_action(act, provider, attrname)
        action_group.add_action(a)
        if act.shortcut:
            key, mod = Gtk.accelerator_parse(act.shortcut)
            accel_group.connect(
                key, mod, Gtk.AccelFlags.VISIBLE, _accel_handler(scope, act.name)
            )
    return ActionGroup(actions=action_group, shortcuts=accel_group)


def create_gio_action(act, provider, attrname):
    if act.state is not None:
        a = Gio.SimpleAction.new_stateful(
            act.name, as_variant_type(act.arg_type), to_variant(act.state)
        )
        a.connect("change-state", _action_activate, provider, attrname)
    else:
        a = Gio.SimpleAction.new(act.name, as_variant_type(act.arg_type))
        a.connect("activate", _action_activate, provider, attrname)
    return a


def iter_actions(provider, scope):
    provider_class = type(provider)
    for attrname in dir(provider_class):
        method = getattr(provider_class, attrname)
        act = getattr(method, "__action__", None)
        if act and act.scope == scope:
            yield (attrname, act)


def set_action_state(action_group, action_name, state):
    action_group.lookup_action(action_name).set_state(
        GLib.Variant.new_boolean(bool(state))
    )


_GVARIANT_TYPE_STR = GLib.VariantType.new("s")
_GVARIANT_TYPE_INT = GLib.VariantType.new("i")
_GVARIANT_TYPE_BOOL = GLib.VariantType.new("b")


def as_variant_type(t):
    if t is None:
        return None
    elif t is str:
        return _GVARIANT_TYPE_STR
    elif t is int:
        return _GVARIANT_TYPE_INT
    elif t is bool:
        return _GVARIANT_TYPE_BOOL
    else:
        raise ValueError(f"No GVariantType declared for Python type {t}")


def to_variant(v):
    if v is None:
        return None
    elif isinstance(v, str):
        return GLib.Variant.new_string(v)
    elif isinstance(v, bool):
        return GLib.Variant.new_boolean(v)
    elif isinstance(v, int):
        return GLib.Variant.new_int32(v)
    else:
        raise ValueError(
            f"No GVariant mapping declared for Python value {v} of type {type(v)}"
        )


def from_variant(v):
    if v is None:
        return None
    elif _GVARIANT_TYPE_STR.equal(v.get_type()):
        return v.get_string()
    elif _GVARIANT_TYPE_INT.equal(v.get_type()):
        return v.get_int32()
    elif _GVARIANT_TYPE_BOOL.equal(v.get_type()):
        return v.get_boolean()
    else:
        raise ValueError(f"No Python mapping declared for GVariant value {v}")


def _action_activate(action, param, obj, name):
    method = getattr(obj, name)
    if param is not None:
        method(from_variant(param))
        if action.get_state_type():
            action.set_state(param)
    else:
        method()
