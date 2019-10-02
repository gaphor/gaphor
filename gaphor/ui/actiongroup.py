from gi.repository import GLib, Gio
from gaphor.abc import ActionProvider
from gaphor.action import action, toggle_action, radio_action


def apply_application_actions(component_registry, gtk_app):
    for provider, _name in component_registry.all(ActionProvider):
        add_actions_to_group(gtk_app, provider, "app")
    return gtk_app


def window_action_group(component_registry):
    action_group = Gio.SimpleActionGroup.new()
    for provider, _name in component_registry.all(ActionProvider):
        add_actions_to_group(action_group, provider, "win")
    return action_group


def add_actions_to_group(
    action_group: Gio.ActionMap, provider, scope: str
) -> Gio.ActionMap:
    for attrname, act in iter_actions(provider, scope):
        if isinstance(act, radio_action):
            a = Gio.SimpleAction.new_stateful(
                act.name, None, GLib.Variant.new_int16(act.active)
            )
            a.connect("change-state", _radio_action_activate, provider, attrname)
        elif isinstance(act, toggle_action):
            a = Gio.SimpleAction.new_stateful(
                act.name, None, GLib.Variant.new_boolean(act.active)
            )
            a.connect("change-state", _toggle_action_activate, provider, attrname)
        elif isinstance(act, action):
            a = Gio.SimpleAction.new(act.name, None)
            a.connect("activate", _action_activate, provider, attrname)
        else:
            raise ValueError(f"Action is not of a known action type ({act})")
        action_group.add_action(a)
    return action_group


def iter_actions(provider, scope):
    provider_class = type(provider)
    for attrname in dir(provider_class):
        method = getattr(provider_class, attrname)
        act = getattr(method, "__action__", None)
        if act and act.scope == scope:
            yield (attrname, act)


def _action_activate(_action, _param, obj, name):
    method = getattr(obj, name)
    method()


def _toggle_action_activate(action, param, obj, name):
    method = getattr(obj, name)
    action.set_state(param)
    method(param.get_boolean())


def _radio_action_activate(action, param, obj, name):
    method = getattr(obj, name)
    action.set_state(param)
    method(param.get_int16())
