from gi.repository import GLib, Gio
from gaphor.abc import ActionProvider
from gaphor.action import action, toggle_action, radio_action


def apply_application_actions(component_registry, gtk_app):
    return action_group_for_scope(component_registry, gtk_app, "app")


def window_action_group(component_registry):
    return action_group_for_scope(
        component_registry, Gio.SimpleActionGroup.new(), "win"
    )


def action_group_for_scope(component_registry, action_group, scope):
    for provider, _name in component_registry.all(ActionProvider):
        provider_class = type(provider)
        for attrname in dir(provider_class):
            method = getattr(provider_class, attrname)
            act = getattr(method, "__action__", None)
            if not act or act.scope != scope:
                continue

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
