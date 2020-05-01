import itertools
from typing import Dict, List, NamedTuple

from gaphor.diagram.copypaste import (
    ElementCopy,
    copy,
    copy_element,
    paste,
    paste_element,
)
from gaphor.UML import Association, Class, Interface


class ClassCopy(NamedTuple):
    element_copy: ElementCopy
    owned_attributes: List[ElementCopy]
    owned_parameters: List[ElementCopy]
    owned_operations: List[ElementCopy]


@copy.register(Class)
@copy.register(Interface)
def copy_class(element):
    return ClassCopy(
        element_copy=copy_element(element),
        owned_attributes=[
            copy_element(attr)
            for attr in element.ownedAttribute
            if not attr.association
        ],
        owned_parameters=[
            copy_element(oper)
            for oper in itertools.chain(
                element.ownedOperation[:].formalParameter,  # type: ignore[attr-defined]
                element.ownedOperation[:].returnResult,  # type: ignore[attr-defined]
            )
        ],
        owned_operations=[copy_element(oper) for oper in element.ownedOperation],
    )


@paste.register
def paste_class(copy_data: ClassCopy, diagram, lookup):
    for attr in itertools.chain(
        copy_data.owned_attributes,
        copy_data.owned_parameters,
        copy_data.owned_operations,
    ):
        paste_element(attr, diagram, lookup)
    return paste_element(copy_data.element_copy, diagram, lookup)


class AssociationCopy(NamedTuple):
    element_copy: ElementCopy
    member_ends: List[ElementCopy]


@copy.register
def copy_association(element: Association):
    return AssociationCopy(
        element_copy=copy_element(element),
        member_ends=[copy_element(end) for end in element.memberEnd],
    )


@paste.register
def paste_association(copy_data: AssociationCopy, diagram, lookup):
    for member_end in copy_data.member_ends:
        paste_element(member_end, diagram, lookup)
    return paste_element(copy_data.element_copy, diagram, lookup)
