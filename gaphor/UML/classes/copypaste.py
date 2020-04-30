from typing import Dict, List, NamedTuple

from gaphor.diagram.copypaste import (
    ElementCopy,
    copy,
    copy_element,
    paste,
    paste_element,
)
from gaphor.UML import Association


class AssociationCopy(NamedTuple):
    element_copy: ElementCopy
    member_ends: List[ElementCopy]


@copy.register
def copy_association(element: Association):
    element_copy = copy_element(element)
    member_ends = [copy_element(end) for end in element.memberEnd]
    return AssociationCopy(element_copy=element_copy, member_ends=member_ends)


@paste.register
def paste_association(copy_data: AssociationCopy, diagram, lookup):
    for member_end in copy_data.member_ends:
        paste_element(member_end, diagram, lookup)
    return paste_element(copy_data.element_copy, diagram, lookup)
