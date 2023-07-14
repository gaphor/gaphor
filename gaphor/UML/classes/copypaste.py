import itertools

from gaphor.diagram.copypaste import copy
from gaphor.UML import (
    Association,
    Class,
    DataType,
    Enumeration,
    Interface,
    Operation,
    Package,
)
from gaphor.UML.copypaste import copy_named_element


@copy.register(Class)
@copy.register(DataType)
@copy.register(Interface)
def copy_class(element):
    yield element.id, copy_named_element(element)
    for feature in itertools.chain(
        element.ownedAttribute,
        element.ownedOperation,
    ):
        yield from copy(feature)


@copy.register
def copy_enumeration(element: Enumeration):
    yield element.id, copy_named_element(element)
    for feature in itertools.chain(
        element.ownedAttribute,
        element.ownedOperation,
        element.ownedLiteral,
    ):
        yield from copy(feature)


@copy.register
def copy_operation(element: Operation):
    yield element.id, copy_named_element(element)
    for feature in element.ownedParameter:
        yield from copy(feature)


@copy.register
def copy_association(element: Association):
    yield element.id, copy_named_element(element)
    for end in element.memberEnd:
        yield from copy(end)


@copy.register
def copy_package(element: Package):
    yield element.id, copy_named_element(element)
    for owned in itertools.chain(
        element.ownedType, element.ownedDiagram, element.ownedRule
    ):
        yield from copy(owned)
