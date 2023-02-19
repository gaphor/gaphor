from functools import singledispatch

from gaphor.core.modeling.coremodel import ElementChange, RefChange, ValueChange


@singledispatch
def apply_change(change, element_factory, modeling_factory, diagram=None):
    raise NotImplementedError


@apply_change.register
def apply_element_change(
    change: ElementChange, element_factory, modeling_factory, diagram=None
):
    if change.applied:
        return
    if change.op == "add" and not change.applied:
        element_type = modeling_factory.lookup_element(change.element_name)
        element_factory.create_as(element_type, change.element_id, diagram=diagram)
    elif change.op == "remove" and not change.applied:
        if element := element_factory.lookup(change.element_id):
            element.unlink()
    change.applied = True


@apply_change.register
def apply_value_change(
    change: ValueChange, element_factory, modeling_factory, diagram=None
):
    if change.applied:
        return
    element = element_factory[change.element_id]
    setattr(element, change.property_name, change.property_value)
    change.applied = True


@apply_change.register
def apply_ref_change(
    change: RefChange, element_factory, modeling_factory, diagram=None
):
    if change.applied:
        return
    element = element_factory[change.element_id]
    ref = element_factory[change.property_ref]
    if change.op in ("add", "update"):
        setattr(element, change.property_name, ref)
    elif change.op == "remove":
        if getattr(type(element), change.property_name).upper == 1:
            delattr(element, change.property_name)
        else:
            getattr(element, change.property_name).remove(ref)
    change.applied = True
