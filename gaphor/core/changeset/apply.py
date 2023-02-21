from functools import singledispatch

from gaphor.core.modeling.coremodel import (
    ElementChange,
    RefChange,
    ValueChange,
)


@singledispatch
def applicable(change) -> bool:
    raise NotImplementedError


@singledispatch
def apply_change(change, element_factory, modeling_factory):
    raise NotImplementedError


@applicable.register
def _(change: ElementChange, element_factory) -> bool:
    if change.diagram_id and not element_factory.lookup(change.diagram_id):
        return False
    element = element_factory.lookup(change.element_id)
    return not bool(element) if change.op == "add" else bool(element)


@apply_change.register
def _(change: ElementChange, element_factory, modeling_factory):
    if change.applied:
        return
    if change.op == "add" and not change.applied:
        element_type = modeling_factory.lookup_element(change.element_name)
        diagram = (
            element_factory.lookup(change.diagram_id) if change.diagram_id else None
        )
        element_factory.create_as(element_type, change.element_id, diagram=diagram)
    elif change.op == "remove" and not change.applied:
        if element := element_factory.lookup(change.element_id):
            element.unlink()
    change.applied = True


@applicable.register
def _(change: ValueChange, element_factory):
    element = element_factory.lookup(change.element_id)
    return bool(
        element and getattr(element, change.property_name) != change.property_value
    )


@apply_change.register
def _(change: ValueChange, element_factory, modeling_factory):
    if change.applied:
        return
    element = element_factory[change.element_id]
    setattr(element, change.property_name, change.property_value)
    change.applied = True


@applicable.register
def _(change: RefChange, element_factory):
    element = element_factory.lookup(change.element_id)
    ref = element_factory.lookup(change.property_ref)
    return bool(element and ref)


@apply_change.register
def _(change: RefChange, element_factory, modeling_factory):
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
