from functools import singledispatch

from gaphor.core.modeling.coremodel import ElementChange, RefChange, ValueChange

ADD = 1
REMOVE = 2
UPDATE = 3


@singledispatch
def apply_change(change, element_factory, modeling_factory, diagram=None):
    raise NotImplementedError


@apply_change.register
def apply_element_change(
    change: ElementChange, element_factory, modeling_factory, diagram=None
):
    if change.op == ADD:
        element_type = modeling_factory.lookup_element(change.element_name)
        return element_factory.create_as(
            element_type, change.element_id, diagram=diagram
        )
    elif change.op == REMOVE:
        if element := element_factory.lookup(change.element_id):
            element.unlink()


@apply_change.register
def apply_value_change(
    change: ValueChange, element_factory, modeling_factory, diagram=None
):
    element = element_factory[change.element_id]
    setattr(element, change.property_name, change.property_value)


@apply_change.register
def apply_ref_change(
    change: RefChange, element_factory, modeling_factory, diagram=None
):
    element = element_factory[change.element_id]
    ref = element_factory[change.property_ref]
    if change.op in (ADD, UPDATE):
        setattr(element, change.property_name, ref)
    elif change.op == REMOVE:
        if getattr(type(element), change.property_name).upper == 1:
            delattr(element, change.property_name)
        else:
            getattr(element, change.property_name).remove(ref)
