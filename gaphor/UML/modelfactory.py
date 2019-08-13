"""
UML model support functions.

Functions collected in this module allow to

- create more complex UML model structures
- perform specific searches and manipulations

"""

from typing import Sequence, Iterable
import itertools
from gaphor.UML.uml2 import *


def stereotypes_str(element: Element, stereotypes: Sequence[str] = ()):
    """
    Identify stereotypes of an UML metamodel instance and return coma
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
    s = ", ".join(itertools.chain(stereotypes, applied))
    if s:
        return f"«{s}»"
    else:
        return ""


def stereotype_name(stereotype):
    """
    Return stereotype name suggested by UML specification. First will be
    character lowercase unless the second character is uppercase.

    :Parameters:
     stereotype
        Stereotype UML metamodel instance.
    """
    name = stereotype.name
    if not name:
        return ""
    elif len(name) > 1 and name[1].isupper():
        return name
    else:
        return name[0].lower() + name[1:]


def apply_stereotype(element, stereotype):
    """
    Apply a stereotype to an element.

    :Parameters:
     element
        UML metamodel class instance.
     stereotype
        UML metamodel stereotype instance.
    """
    assert (
        element.model is stereotype.model
    ), "Element and Stereotype are from different models"
    model = element.model
    obj = model.create(InstanceSpecification)
    obj.classifier = stereotype
    element.appliedStereotype = obj
    return obj


def find_instances(element):
    """
    Find instance specification which extend classifier `element`.
    """
    model = element.model
    return model.select(
        lambda e: e.isKindOf(InstanceSpecification)
        and e.classifier
        and e.classifier[0] == element
    )


def remove_stereotype(element, stereotype):
    """
    Remove a stereotype from an element.

    :Parameters:
     element
        UML metamodel element instance.
     stereotype
        UML metamodel stereotype instance.
    """
    for obj in element.appliedStereotype:
        if obj.classifier and obj.classifier[0] is stereotype:
            del element.appliedStereotype[obj]
            obj.unlink()
            break


def get_stereotypes(element):
    """
    Get sorted collection of possible stereotypes for specified element.
    """
    model = element.model
    # UML specs does not allow to extend stereotypes with stereotypes
    if isinstance(element, Stereotype):
        return ()

    cls = type(element)

    # find out names of classes, which are superclasses of element class
    names = {c.__name__ for c in cls.__mro__ if issubclass(c, Element)}

    # find stereotypes that extend element class
    classes = model.select(lambda e: e.isKindOf(Class) and e.name in names)

    stereotypes = {ext.ownedEnd.type for cls in classes for ext in cls.extension}
    return sorted(stereotypes, key=lambda st: st.name)


def get_applied_stereotypes(element):
    """
    Get collection of applied stereotypes to an element.
    """
    return element.appliedStereotype[:].classifier


def create_extension(metaclass, stereotype):
    """
    Create an Extension association between an metaclass and a stereotype.
    """
    assert (
        metaclass.model is stereotype.model
    ), "Metaclass and Stereotype are from different models"

    model = metaclass.model
    ext = model.create(Extension)
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


def is_metaclass(element):
    return (
        (not isinstance(element, Stereotype))
        and hasattr(element, "extension")
        and bool(element.extension)
    )


def add_slot(instance, definingFeature):
    """
    Add slot to instance specification for an attribute.
    """
    assert (
        instance.model is definingFeature.model
    ), "Instance and Defining feature are from different models"
    model = instance.model
    slot = model.create(Slot)
    slot.definingFeature = definingFeature
    instance.slot = slot
    return slot


def create_dependency(supplier, client):
    assert (
        supplier.model is client.model
    ), "Supplier and Client are from different models"
    model = supplier.model
    dep = model.create(Dependency)
    dep.supplier = supplier
    dep.client = client
    return dep


def create_realization(realizingClassifier, abstraction):
    assert (
        realizingClassifier.model is abstraction.model
    ), "Realizing classifier and Abstraction are from different models"
    model = realizingClassifier.model
    dep = model.create(Realization)
    dep.realizingClassifier = realizingClassifier
    dep.abstraction = abstraction
    return dep


def create_generalization(general, specific):
    assert (
        general.model is specific.model
    ), "General and Specific are from different models"
    model = general.model
    gen = model.create(Generalization)
    gen.general = general
    gen.specific = specific
    return gen


def create_implementation(contract, implementatingClassifier):
    assert (
        contract.model is implementatingClassifier.model
    ), "Contract and Implementating classifier are from different models"
    model = contract.model
    impl = model.create(Implementation)
    impl.contract = contract
    impl.implementatingClassifier = implementatingClassifier
    return impl


def create_association(type_a, type_b):
    """
    Create an association between two items.
    """
    assert type_a.model is type_b.model, "Head and Tail end are from different models"
    model = type_a.model
    assoc = model.create(Association)
    end_a = model.create(Property)
    end_b = model.create(Property)
    assoc.memberEnd = end_a
    assoc.memberEnd = end_b
    end_a.type = type_a
    end_b.type = type_b
    # set default navigability (unknown)
    set_navigability(assoc, end_a, None)
    set_navigability(assoc, end_b, None)
    return assoc


def set_navigability(assoc, end, nav):
    """
    Set navigability of an association end (property).

    There are three possible values for ``nav`` parameter

     True
        association end is navigable
     False
        association end is not navigable
     None
        association end navigability is unkown

    There are two ways of specifing that an end is navigable

    - an end is in Association.navigableOwnedEnd collection
    - an end is class (interface) attribute (stored in Class.ownedAttribute
      collection)

    Let's consider the graph::

        A -----> B
          y    x

    There two association ends A.x and B.y, A.x is navigable.

    Therefore navigable association ends are constructed in following way

    - if A is a class or an interface, then A.x is an attribute owned by A
    - if A is other classifier, then association is more general
      relationship; it may mean that participating instance of B can be
      "accessed efficiently"
      - i.e. when A is a Component, then association may be some compositing
        relationship
      - when A and B are instances of Node class, then it is a
        communication path

    Therefore navigable association end may be stored as one of
    - {Class,Interface}.ownedAttribute due to their capabilities of
      editing owned members
    - Association.navigableOwnedEnd

    When an end has unknown (unspecified) navigability, then it is owned by
    association (but not by classifier).

    When an end is non-navigable, then it is just member of an association.
    """
    # remove "navigable" and "unspecified" navigation indicators first
    if type(end.type) in (Class, Interface):
        owner = end.opposite.type
        if end in owner.ownedAttribute:
            owner.ownedAttribute.remove(end)
    if end in assoc.ownedEnd:
        assoc.ownedEnd.remove(end)
    if end in assoc.navigableOwnedEnd:
        assoc.navigableOwnedEnd.remove(end)
    assert end not in assoc.ownedEnd
    assert end not in assoc.navigableOwnedEnd

    if nav is True:
        if type(end.type) in (Class, Interface):
            owner = end.opposite.type
            owner.ownedAttribute = end
        else:
            assoc.navigableOwnedEnd = end
    elif nav is None:
        assoc.ownedEnd = end
    # elif nav is False, non-navigable


def dependency_type(client, supplier):
    """
    Determine dependency type between client (tail) and supplier
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
    elif isinstance(client, Component) and isinstance(supplier, Classifier):
        dt = Realization

    return dt


def clone_message(msg, inverted=False):
    """
    Create new message based on speciied message.

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
        # inverted message goes in different direction, than original
        # message
        message.sendEvent = receive
        message.receiveEvent = send
    else:
        message.sendEvent = send
        message.receiveEvent = receive
    return message


def swap_element(element, new_class):
    """
    A "trick" to swap the element type.

    Used in certain cases where the underlaying element type
    may change.
    """
    if element.__class__ is not new_class:
        element.__class__ = new_class
