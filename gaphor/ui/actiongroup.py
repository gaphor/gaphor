from __future__ import annotations

import sys
from typing import NamedTuple

from gi.repository import Gio, GLib, Gtk

from gaphor.abc import ActionProvider
from gaphor.action import action


def apply_application_actions(component_registry, gtk_app):
    scope = "app"
    for _name, provider in component_registry.all(ActionProvider):
        for attrname, act in iter_actions(provider, scope):
            a = create_gio_action(act, provider, attrname)
            gtk_app.add_action(a)
            if act.shortcut:
                gtk_app.set_accels_for_action(
                    f"{scope}.{act.name}",
                    [_platform_specific(s) for s in act.shortcuts],
                )
    return gtk_app


class ActionGroup(NamedTuple):
    actions: Gio.SimpleActionGroup
    shortcuts: Gio.ListModel


def window_action_group(component_registry) -> ActionGroup:
    action_group = Gio.SimpleActionGroup.new()
    store = Gio.ListStore.new(Gtk.Shortcut)
    scope = "win"
    for _name, provider in component_registry.all(ActionProvider):
        for attrname, act in iter_actions(provider, scope):
            a = create_gio_action(act, provider, attrname)
            action_group.add_action(a)
            for shortcut in act.shortcuts:
                store.append(
                    _new_shortcut(_platform_specific(shortcut), act.detailed_name)
                )
    return ActionGroup(actions=action_group, shortcuts=store)


def create_action_group(provider, scope) -> ActionGroup:
    action_group = Gio.SimpleActionGroup.new()
    store = Gio.ListStore.new(Gtk.Shortcut)
    for attrname, act in iter_actions(provider, scope):
        a = create_gio_action(act, provider, attrname)
        action_group.add_action(a)
        for shortcut in act.shortcuts:
            store.append(_new_shortcut(_platform_specific(shortcut), act.detailed_name))
    return ActionGroup(actions=action_group, shortcuts=store)


def _platform_specific(shortcut):
    return shortcut.replace(
        "<Primary>", "<Meta>" if sys.platform == "darwin" else "<Control>"
    )


def _new_shortcut(shortcut, detailed_name):
    return Gtk.Shortcut.new(
        trigger=Gtk.ShortcutTrigger.parse_string(shortcut),
        action=Gtk.NamedAction.new(detailed_name),
    )


def create_gio_action(act, provider, attrname):
    if act.state is not None:
        state = act.state(provider) if callable(act.state) else act.state
        a = Gio.SimpleAction.new_stateful(
            act.name, as_variant_type(act.arg_type), to_variant(state)
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
        act: action | None = getattr(method, "__action__", None)
        if act and act.scope == scope:
            yield (attrname, act)


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
