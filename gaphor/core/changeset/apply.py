from functools import singledispatch

from gaphor.core.modeling.coremodel import (
    ElementChange,
    RefChange,
    ValueChange,
)


@singledispatch
def applicable(change, element_factory) -> bool:
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
    if change.op == "add":
        element_type = modeling_factory.lookup_element(change.element_name)
        diagram = (
            element_factory.lookup(change.diagram_id) if change.diagram_id else None
        )
        element_factory.create_as(element_type, change.element_id, diagram=diagram)
    elif change.op == "remove":
        if element := element_factory.lookup(change.element_id):
            element.unlink()
    change.applied = True


@applicable.register
def _(change: ValueChange, element_factory):
    element = element_factory.lookup(change.element_id)
    return bool(
        element
        and getattr(element, change.property_name, None) != change.property_value
    )


@apply_change.register
def _(change: ValueChange, element_factory, modeling_factory):
    if change.applied:
        return
    element = element_factory[change.element_id]
    element.load(change.property_name, change.property_value)
    element.postload()
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
    prop = getattr(type(element), change.property_name, None)
    if change.op in ("add", "update"):
        element.load(change.property_name, ref)
        element.postload()
    elif change.op == "remove" and prop:
        if prop.upper == 1:
            delattr(element, change.property_name)
        else:
            getattr(element, change.property_name).remove(ref)
    change.applied = True

    if prop and prop.opposite:
        if other := next(
            element_factory.select(
                lambda e: isinstance(e, RefChange)
                and e.element_id == change.property_ref
                and e.property_ref == change.element_id
                and e.property_name == prop.opposite
            ),
            None,
        ):
            other.applied = True
