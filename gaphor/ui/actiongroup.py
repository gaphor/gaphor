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
                act.name,
                as_variant_type(act.arg_type),
                GLib.Variant.new_int16(act.active),
            )
            a.connect("change-state", _radio_action_activate, provider, attrname)
        elif isinstance(act, toggle_action):
            a = Gio.SimpleAction.new_stateful(
                act.name,
                as_variant_type(act.arg_type),
                GLib.Variant.new_boolean(act.active),
            )
            a.connect("change-state", _toggle_action_activate, provider, attrname)
        elif isinstance(act, action):
            a = Gio.SimpleAction.new(act.name, as_variant_type(act.arg_type))
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
    # param = action.get_attribute_value("param", GLib.VariantType.new("s"))
    print(f"Action {name} with param {param}")
    method = getattr(obj, name)
    if param:
        method(param)
    else:
        method()


def _toggle_action_activate(action, param, obj, name):
    method = getattr(obj, name)
    action.set_state(param)
    method(param.get_boolean())


def _radio_action_activate(action, param, obj, name):
    method = getattr(obj, name)
    action.set_state(param)
    method(param.get_int16())
