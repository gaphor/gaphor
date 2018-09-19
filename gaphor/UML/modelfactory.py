#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License 
# more details.
#
# You should have received a copy of the GNU Library General Public 
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
UML model support functions.

Functions collected in this module allow to

- create more complex UML model structures
- perform specific searches and manipulations

"""

from __future__ import absolute_import
from gaphor.UML.uml2 import *

# '<<%s>>'
STEREOTYPE_FMT = '\xc2\xab%s\xc2\xbb'

def stereotypes_str(element, stereotypes=()):
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
        applied = (stereotype_name(st) for st in get_applied_stereotypes(element))
    else:
        applied = ()
    s = ', '.join(itertools.chain(stereotypes, applied))
    if s:
        return STEREOTYPE_FMT % s
    else:
        return ''


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
        return ''
    elif len(name) > 1 and name[1].isupper():
        return name
    else:
        return name[0].lower() + name[1:]


def apply_stereotype(factory, element, stereotype):
    """
    Apply a stereotype to an element.

    :Parameters:
     factory
        UML metamodel factory.
     element
        UML metamodel class instance.
     stereotype
        UML metamodel stereotype instance.
    """
    obj = factory.create(InstanceSpecification)
    obj.classifier = stereotype
    element.appliedStereotype = obj
    return obj


def find_instances(factory, element):
    """
    Find instance specification which extend classifier `element`.
    """
    return factory.select(lambda e: e.isKindOf(InstanceSpecification) \
            and e.classifier and e.classifier[0] == element)


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


def get_stereotypes(factory, element):
    """
    Get sorted collection of possible stereotypes for specified element.
    """
    # UML specs does not allow to extend stereotypes with stereotypes
    if isinstance(element, Stereotype):
        return ()

    cls = type(element)

    # find out names of classes, which are superclasses of element class
    names = set(c.__name__ for c in cls.__mro__ if issubclass(c, Element))

    # find stereotypes that extend element class
    classes = factory.select(lambda e: e.isKindOf(Class) and e.name in names)
    
    stereotypes = set(ext.ownedEnd.type for cls in classes for ext in cls.extension)
    return sorted(stereotypes, key=lambda st: st.name)


def get_applied_stereotypes(element):
    """
    Get collection of applied stereotypes to an element.
    """
    return element.appliedStereotype[:].classifier


def create_extension(factory, element, stereotype):
    """
    Extend an element with a stereotype.
    """
    ext = factory.create(Extension)
    p = factory.create(Property)
    ext_end = factory.create(ExtensionEnd)

    ext.memberEnd = p
    ext.memberEnd = ext_end
    ext.ownedEnd = ext_end
    ext_end.type = stereotype
    ext_end.aggregation = 'composite'
    p.type = element
    p.name = 'baseClass'
    stereotype.ownedAttribute = p

    return ext

extend_with_stereotype = create_extension

def add_slot(factory, instance, definingFeature):
    """
    Add slot to instance specification for an attribute.
    """
    slot = factory.create(Slot)
    slot.definingFeature = definingFeature
    instance.slot = slot
    return slot


def create_dependency(factory, supplier, client):
    dep = factory.create(Dependency)
    dep.supplier = supplier
    dep.client = client
    return dep

def create_realization(factory, realizingClassifier, abstraction):
    dep = factory.create(Realization)
    dep.realizingClassifier = realizingClassifier
    dep.abstraction = abstraction
    return dep

def create_generalization(factory, general, specific):
    gen = factory.create(Generalization)
    gen.general = general
    gen.specific = specific
    return gen

def create_implementation(factory, contract, implementatingClassifier):
    impl = factory.create(Implementation)
    impl.contract = contract
    impl.implementatingClassifier = implementatingClassifier
    return impl

def create_association(factory, type_a, type_b):
    """
    Create an association between two items.
    """
    assoc = factory.create(Association)
    end_a = factory.create(Property)
    end_b = factory.create(Property)
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

    There are free possible values for ``nav`` parameter

     True
        association end is navigable
     False
        association end is not navigable
     None
        association end navigability is unkown

    There are two ways of specifing than an end is navigable

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


def create_message(factory, msg, inverted=False):
    """
    Create new message based on speciied message.

    If inverted is set to True, then inverted message is created.
    """
    message = factory.create(Message)
    send = None
    receive = None

    if msg.sendEvent:
        send = factory.create(MessageOccurrenceSpecification)
        sl = msg.sendEvent.covered
        send.covered = sl
    if msg.receiveEvent:
        receive = factory.create(MessageOccurrenceSpecification)
        rl = msg.receiveEvent.covered
        receive.covered = rl

    if inverted:
        # inverted message goes in different direction, than original
        # message
        message.sendEvent = receive
        message.receiveEvent = send
    else:
        message.sendEvent = send
        message.receiveEvent = receive
    return message


#vim:sw=4:et:ai
