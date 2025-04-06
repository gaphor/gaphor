from __future__ import annotations

import sys
from itertools import chain

from gi.repository import Gio, GLib, Gtk

from gaphor.abc import ActionProvider
from gaphor.action import action
from gaphor.entrypoint import load_entry_points


def apply_application_actions(component_registry, gtk_app) -> None:
    scope = "app"
    for _name, provider in component_registry.all(ActionProvider):
        for attrname, act in iter_actions(type(provider), scope):
            a = create_gio_action(act, provider, attrname)
            gtk_app.add_action(a)


def apply_shortcuts_from_entry_point(
    entry_point, scope, gtk_app, *, extra=None
) -> None:
    for provider_class in chain(load_entry_points(entry_point).values(), extra or []):
        if not issubclass(provider_class, ActionProvider):
            continue
        for _attrname, act in iter_actions(provider_class, scope):
            if act.shortcut:
                gtk_app.set_accels_for_action(
                    f"{scope}.{act.name}",
                    [_platform_modifier(s) for s in act.shortcuts],
                )


def window_action_group(component_registry, scope="win") -> Gio.SimpleActionGroup:
    action_group = Gio.SimpleActionGroup.new()
    for _name, provider in component_registry.all(ActionProvider):
        for attrname, act in iter_actions(type(provider), scope):
            a = create_gio_action(act, provider, attrname)
            action_group.add_action(a)
    return action_group


def apply_action_group(provider, scope, target_widget):
    action_group, shortcuts = create_action_group_and_shortcuts(provider, scope)
    target_widget.insert_action_group(scope, action_group)
    target_widget.add_controller(shortcuts)


def create_action_group_and_shortcuts(
    provider, scope
) -> tuple[Gio.SimpleActionGroup, Gtk.ShortcutController]:
    action_group = Gio.SimpleActionGroup.new()
    store = Gio.ListStore.new(Gtk.Shortcut)
    for attrname, act in iter_actions(type(provider), scope):
        a = create_gio_action(act, provider, attrname)
        action_group.add_action(a)
        for shortcut in act.shortcuts:
            store.append(named_shortcut(shortcut, act.detailed_name))

    ctrl = Gtk.ShortcutController.new_for_model(store)
    ctrl.set_scope(Gtk.ShortcutScope.LOCAL)
    return (action_group, ctrl)


def named_shortcut(shortcut, detailed_name):
    return Gtk.Shortcut.new(
        trigger=Gtk.ShortcutTrigger.parse_string(_platform_modifier(shortcut)),
        action=Gtk.NamedAction.new(detailed_name),
    )


def _platform_modifier(shortcut):
    return shortcut.replace(
        "<Primary>", "<Meta>" if sys.platform == "darwin" else "<Control>"
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


def iter_actions(provider_class, scope):
    for attrname in dir(provider_class):
        func = getattr(provider_class, attrname)
        if callable(func):
            act: action | None = getattr(func, "__action__", None)
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
