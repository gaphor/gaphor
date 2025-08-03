"""UML model support functions.

Functions collected in this module allow to

- create more complex UML model structures
- perform specific searches and manipulations
"""

from __future__ import annotations

import itertools
from collections.abc import Iterable, Sequence

from gaphor.core.modeling import UnlimitedNatural
from gaphor.diagram.group import owner_of_type
from gaphor.UML.uml import (
    Artifact,
    Association,
    Class,
    Classifier,
    Component,
    ConnectableElement,
    Connector,
    ConnectorEnd,
    DataType,
    Dependency,
    Element,
    Extension,
    ExtensionEnd,
    Generalization,
    InstanceSpecification,
    Interface,
    LiteralBoolean,
    LiteralInteger,
    LiteralString,
    LiteralUnlimitedNatural,
    Message,
    MessageOccurrenceSpecification,
    MultiplicityElement,
    Package,
    Parameter,
    Port,
    Property,
    Realization,
    Slot,
    Stereotype,
    StructuralFeature,
    StructuredClassifier,
    Type,
    Usage,
    ValueSpecification,
)


def stereotypes_str(element: Element, stereotypes: Sequence[str] = ()) -> str:
    """Identify stereotypes of a UML metamodel instance and return coma
    separated stereotypes as string.

    :Parameters:
     element
        Element having stereotypes, can be None.
     stereotypes
        List of additional stereotypes, can be empty.
    """
    # generate string with stereotype names separated by coma
    if element:
        applied: Iterable[str] = (
            stereotype_name(st) for st in get_applied_stereotypes(element)
        )
    else:
        applied = ()
    if s := ", ".join(itertools.chain(stereotypes, applied)):
        return f"«{s}»"
    return ""


def stereotype_name(stereotype: Stereotype) -> str:
    """Return stereotype name suggested by UML specification. First will be
    character lowercase unless the second character is uppercase.

    :Parameters:
     stereotype
        Stereotype UML metamodel instance.
    """
    name: str = stereotype.name
    if not name:
        return ""
    elif len(name) > 1 and name[1].isupper():
        return name
    return name[0].lower() + name[1:]


def apply_stereotype(element: Element, stereotype: Stereotype) -> InstanceSpecification:
    """Apply a stereotype to an element.

    :Parameters:
     element
        UML metamodel class instance.
     stereotype
        UML metamodel stereotype instance.
    """
    assert element.model is stereotype.model, (
        "Element and Stereotype are from different models"
    )
    model = element.model
    obj = model.create(InstanceSpecification)
    obj.classifier = stereotype
    element.appliedStereotype = obj
    return obj


def remove_stereotype(element: Element, stereotype: Stereotype) -> None:
    """Remove a stereotype from an element.

    :Parameters:
     element
        UML metamodel element instance.
     stereotype
        UML metamodel stereotype instance.
    """
    for obj in element.appliedStereotype:
        assert isinstance(obj, InstanceSpecification)
        if obj.classifier and obj.classifier[0] is stereotype:
            del element.appliedStereotype[obj]
            obj.unlink()
            break


def get_stereotypes(element: Element) -> list[Stereotype]:
    """Get sorted collection of possible stereotypes for specified element."""
    model = element.model
    # UML specs does not allow to extend stereotypes with stereotypes
    if isinstance(element, Stereotype):
        return []

    cls = type(element)

    # find out names of classes, which are superclasses of element class
    names = {c.__name__ for c in cls.__mro__ if issubclass(c, Element)}

    # find stereotypes that extend element class
    classes: Iterable[Class] = model.select(  # type: ignore[assignment]
        lambda e: isinstance(e, Class) and e.name in names
    )

    stereotypes = list({ext.ownedEnd.type for cls in classes for ext in cls.extension})

    all_stereotypes = stereotypes
    for s in stereotypes:
        for sub in s.specialization[:].specific:
            if isinstance(sub, Stereotype) and sub not in all_stereotypes:
                all_stereotypes.append(sub)

    return sorted(all_stereotypes, key=lambda st: st.name)


def get_applied_stereotypes(element: Element) -> Sequence[Stereotype]:
    """Get collection of applied stereotypes to an element."""
    return (
        element.appliedStereotype[:].classifier if isinstance(element, Element) else []  # type: ignore[return-value]
    )


def create_extension(metaclass: Class, stereotype: Stereotype) -> Extension:
    """Create an Extension association between a metaclass and a stereotype."""
    assert metaclass.model is stereotype.model, (
        "Metaclass and Stereotype are from different models"
    )

    model = metaclass.model
    ext: Extension = model.create(Extension)
    p = model.create(Property)
    ext_end = model.create(ExtensionEnd)

    ext.memberEnd = p
    ext.memberEnd = ext_end
    ext.ownedEnd = ext_end
    ext_end.type = stereotype
    ext_end.aggregation = "composite"
    p.type = metaclass
    p.name = "baseClass"
    stereotype.ownedAttribute = p
    metaclass.ownedAttribute = ext_end

    return ext


def is_metaclass(element: Element) -> bool:
    return (
        (not isinstance(element, Stereotype))
        and hasattr(element, "extension")
        and bool(element.extension)
    )


def add_slot(
    instance: InstanceSpecification, definingFeature: StructuralFeature
) -> Slot:
    """Add slot to instance specification for an attribute."""
    assert instance.model is definingFeature.model, (
        "Instance and Defining feature are from different models"
    )
    model = instance.model
    slot = model.create(Slot)
    slot.definingFeature = definingFeature
    instance.slot = slot
    return slot


def get_slot_value(slot: Slot) -> str | None:
    """Get slot value as a string."""
    if slot.value is None:
        return None
    if isinstance(slot.value, LiteralString):
        return str(slot.value.value)
    return None


def set_slot_value(slot: Slot, value: str) -> None:
    """Set slot value to a string."""
    if slot.value:
        slot.value.unlink()
    slot_value = slot.model.create(LiteralString)
    slot.value = slot_value
    slot_value.owningSlot = slot
    slot_value.value = value


def create_dependency(supplier, client):
    assert supplier.model is client.model, (
        "Supplier and Client are from different models"
    )
    model = supplier.model
    dep = model.create(Dependency)
    dep.supplier = supplier
    dep.client = client
    return dep


def create_realization(realizingClassifier, abstraction):
    assert realizingClassifier.model is abstraction.model, (
        "Realizing classifier and Abstraction are from different models"
    )
    model = realizingClassifier.model
    dep = model.create(Realization)
    dep.realizingClassifier = realizingClassifier
    dep.abstraction = abstraction
    return dep


def create_generalization(general, specific):
    assert general.model is specific.model, (
        "General and Specific are from different models"
    )
    model = general.model
    gen = model.create(Generalization)
    gen.general = general
    gen.specific = specific
    return gen


def create_association(type_a: Type, type_b: Type):
    """Create an association between two items."""
    assert type_a.model is type_b.model, "Head and Tail end are from different models"
    model = type_a.model
    assoc = model.create(Association)
    end_a = model.create(Property)
    end_b = model.create(Property)
    end_a.association = assoc
    end_b.association = assoc
    end_a.type = type_a
    end_b.type = type_b
    # set default navigability (unknown)
    set_navigability(assoc, end_a, None)
    set_navigability(assoc, end_b, None)
    return assoc


def create_connector(
    type_a: ConnectableElement, type_b: ConnectableElement
) -> Connector:
    """Create a connector between two items.

    Depending on the ends, the connector kind may be "assembly" or
    "delegation".
    """
    assert type_a.model is type_b.model, "Head and Tail end are from different models"
    model = type_a.model
    conn = model.create(Connector)
    end_a = model.create(ConnectorEnd)
    end_b = model.create(ConnectorEnd)

    conn.end = end_a
    conn.end = end_b

    end_a.role = type_a
    end_b.role = type_b

    if (isinstance(end_a, Port) and isinstance(end_b, Property)) or (
        isinstance(end_a, Property) and isinstance(end_b, Port)
    ):
        conn.kind = "delegation"
    else:
        conn.kind = "assembly"

    return conn


TYPES_WITH_OWNED_ATTRIBUTE = (
    Artifact,
    Class,
    DataType,
    Interface,
    StructuredClassifier,
)


def set_navigability(assoc: Association, end: Property, nav: bool | None) -> None:
    """Set navigability of an association end (property).

    There are three possible values for ``nav`` parameter:
    1. True - association end is navigable
    2. False - association end is not navigable
    3. None - association end navigability is unknown

    There are two ways of specifying that an end is navigable:
    - an end is in Association.navigableOwnedEnd collection
    - an end is class (interface) attribute (stored in Class.ownedAttribute
      collection)

    Let's consider the graph::

        A -----> B
          y    x

    There two association ends A.x and B.y, A.x is navigable.

    Therefore, we construct navigable association ends in the following way:

    - if A is a class or an interface, then A.x is an attribute owned by A
    - if A is other classifier, then association is more general
      relationship; it may mean that participating instance of B can be
      "accessed efficiently"
      - i.e. when A is a Component, then association may be some compositing
        relationship
      - when A and B are instances of Node class, then it is a
        communication path

    Therefore, we store the navigable association end as one of the following:
    - {Class,Interface}.ownedAttribute due to their capabilities of
      editing owned members
    - Association.navigableOwnedEnd

    When an end has unknown (unspecified) navigability, then it is owned by
    association (but not by classifier).

    When an end is non-navigable, then it is just member of an association.
    """
    assert end.opposite
    owner = end.opposite.type
    # remove "navigable" and "unspecified" navigation indicators first
    if isinstance(owner, TYPES_WITH_OWNED_ATTRIBUTE) and end in owner.ownedAttribute:
        owner.ownedAttribute.remove(end)
    if end in assoc.ownedEnd:
        assoc.ownedEnd.remove(end)
    if end in assoc.navigableOwnedEnd:
        assoc.navigableOwnedEnd.remove(end)

    assert end not in assoc.ownedEnd
    assert end not in assoc.navigableOwnedEnd

    if nav is True:
        if isinstance(owner, TYPES_WITH_OWNED_ATTRIBUTE):
            owner.ownedAttribute = end
        else:
            assoc.navigableOwnedEnd = end
    elif nav is None:
        assoc.ownedEnd = end
    # elif nav is False, non-navigable


def dependency_type(client, supplier):
    """Determine dependency type between client (tail) and supplier
    (arrowhead).

    There can be different dependencies detected automatically

    - usage when supplier is an interface
    - realization when client is component and supplier is a classifier

    If none of above is detected then standard dependency is determined.
    """
    dt = Dependency

    # test interface first as it is a classifier
    if isinstance(supplier, Interface):
        dt = Usage
    elif (
        isinstance(supplier, Component)
        and isinstance(client, Classifier)
        and not isinstance(client, Component)
    ):
        dt = Realization

    return dt


def clone_message(msg, inverted=False):
    """Create new message based on specified message.

    If inverted is set to True, then inverted message is created.
    """
    model = msg.model
    message = model.create(Message)
    send = None
    receive = None

    if msg.sendEvent:
        send = model.create(MessageOccurrenceSpecification)
        send.covered = msg.sendEvent.covered
    if msg.receiveEvent:
        receive = model.create(MessageOccurrenceSpecification)
        receive.covered = msg.receiveEvent.covered

    if inverted:
        # inverted message goes in different direction, then the original message
        message.sendEvent = receive
        message.receiveEvent = send
    else:
        message.sendEvent = send
        message.receiveEvent = receive
    return message


def owner_package(element: Element | None) -> Package | None:
    return owner_of_type(element, Package)


def get_literal_value_as_string(value: ValueSpecification) -> str | None:
    """Get literal value as a string."""
    if value is None:
        return None
    if isinstance(value, LiteralUnlimitedNatural):
        return str(value.value)
    if isinstance(value, LiteralInteger):
        return str(value.value)
    if isinstance(value, LiteralString):
        return str(value.value)
    if isinstance(value, LiteralBoolean):
        if value.value is True:
            return "true"
        return "false"
    return None


def create_value_specification_for_type_and_value(
    model, type: str | None, value: str | None
) -> ValueSpecification | None:
    if value is None:
        return None
    if type is None:
        if value == "true" or value == "false":
            type = "bool"
        elif value.isnumeric():
            type = "int"
        else:
            type = "str"
    value_specification: ValueSpecification
    match type:
        case "bool" | "Boolean":
            value_specification = model.create(LiteralBoolean)
            if value == "true":
                value_specification.value = True
                value_specification.name = "true"
            else:
                value_specification.value = False
                value_specification.name = "false"
        case "str" | "String":
            stripped_value = value.replace('"', "")
            value_specification = model.create(LiteralString)
            value_specification.value = value
            value_specification.name = stripped_value
        case "int" | "Integer":
            value_specification = model.create(LiteralInteger)
            value_specification.value = int(value)
            value_specification.name = value
        case "UnlimitedNatural":
            value_specification = model.create(LiteralUnlimitedNatural)
            value_specification.value = value
            value_specification.name = str(value)
        # case "float" | "Real":
        #     value_specification = model.create(LiteralReal)
        #     value_specification.value = float(value)
        case _:
            # If we do not know, cram it in a string
            value_specification = model.create(LiteralString)
            value_specification.value = value
            value_specification.name = value
    return value_specification


def get_multiplicity_lower_value(element: MultiplicityElement) -> int | None:
    """Get lower value of a multiplicity element."""
    if element.lowerValue is None:
        return None
    if isinstance(element.lowerValue, LiteralInteger):
        return int(element.lowerValue.value)
    return None


def get_multiplicity_lower_value_as_string(
    multiplicity: MultiplicityElement,
) -> str | None:
    """Get lower value of a multiplicity as a string."""
    if multiplicity.lowerValue is None:
        return None
    if isinstance(multiplicity.lowerValue, LiteralInteger):
        return str(multiplicity.lowerValue.value)
    return None


def set_multiplicity_lower_value(
    element: MultiplicityElement, value: int | str | None
) -> None:
    """Set lower value of a multiplicity."""
    if element.lowerValue:
        element.lowerValue.unlink()
    if value is None:
        return
    lower_value = element.model.create(LiteralInteger)
    lower_value.value = int(value)
    lower_value.name = str(value)
    element.lowerValue = lower_value


def get_multiplicity_upper_value(
    element: MultiplicityElement,
) -> UnlimitedNatural | None:
    """Get upper value of a parameter."""
    if element.upperValue is None:
        return None
    if isinstance(element.upperValue, LiteralUnlimitedNatural):
        return element.upperValue.value  # type: ignore[no-any-return]
    return None


def get_multiplicity_upper_value_as_string(
    element: MultiplicityElement,
) -> str | None:
    """Get upper value of a multiplicity as a string."""
    if element.upperValue is None:
        return None
    if isinstance(element.upperValue, LiteralUnlimitedNatural):
        return str(element.upperValue.value)
    return None


def set_multiplicity_upper_value(
    element: MultiplicityElement, value: UnlimitedNatural | str | None
) -> None:
    """Set upper value of a multiplicity."""
    if element.upperValue:
        element.upperValue.unlink()
    if value is None:
        return
    upper_value = element.model.create(LiteralUnlimitedNatural)
    upper_value.value = "*" if value == "*" else int(value)
    upper_value.name = str(value)
    element.upperValue = upper_value


def get_default_value_as_string(element: Parameter | Property) -> str | None:
    """Get default value of a parameter as a string."""
    if element.defaultValue is None:
        return None
    return get_literal_value_as_string(element.defaultValue)


def set_default_value_from_string(
    element: Parameter | Property, value: str | None
) -> None:
    """Set default value of a parameter."""
    if element.defaultValue:
        element.defaultValue.unlink()
    if value is None:
        return
    default_value = create_value_specification_for_type_and_value(
        element.model, element.typeValue, value
    )
    element.defaultValue = default_value
