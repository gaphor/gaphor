from functools import singledispatch

from gaphor.core.modeling import UnlimitedNatural
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
        element_type = modeling_factory.lookup_element(
            change.element_name, change.modeling_language
        )
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
        and getattr(element, change.property_name, None)
        != get_value_change_property_value(change)
    )


@apply_change.register
def _(change: ValueChange, element_factory, modeling_factory):
    if change.applied:
        return
    element = element_factory[change.element_id]
    element.load(change.property_name, get_value_change_property_value(change))
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


def get_value_change_property_value(
    value_change,
) -> None | str | int | UnlimitedNatural | bool:
    if value_change.property_value is None:
        return None
    elif value_change.property_type == "str":
        return str(value_change.property_value)
    elif value_change.property_type == "int":
        return int(value_change.property_value)
    elif value_change.property_type == "bool":
        return bool(value_change.property_value == "True")
    elif (
        value_change.property_type == "UnlimitedNatural"
        and value_change.property_value == "*"
    ):
        return "*"
    elif value_change.property_type == "UnlimitedNatural":
        return int(value_change.property_value)
    else:
        return None
