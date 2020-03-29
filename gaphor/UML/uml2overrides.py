"""
Special methods (overrides) that add behavior to the model
that cannot simply be generated.

Derived methods always return a list. Note this is not the case
for normal properties.
"""

from __future__ import annotations

import itertools
from typing import List, Optional, Tuple, Union

import gaphor.UML.uml2 as uml2
import gaphor.UML.umllex as umllex
from gaphor.UML.properties import association, derived


# See https://www.omg.org/spec/UML/2.5/PDF, section 12.4.1.5, page 271
def extension_metaclass(self):
    """
    References the Class that is extended through an Extension. The
    property is derived from the type of the memberEnd that is not the
    ownedEnd.
    """
    ownedEnd = self.ownedEnd
    metaend = [e for e in self.memberEnd if e is not ownedEnd]
    if metaend:
        return metaend[0].type


# Don't use derived() now, it can not deal with a [0..1] property derived from a [0..*] property.
# Extension.metaclass = derived(Extension, 'metaclass', Class, 0, 1, Extension.ownedEnd, Association.memberEnd)
# Extension.metaclass.filter = extension_metaclass
uml2.Extension.metaclass = property(
    extension_metaclass, doc=extension_metaclass.__doc__
)


def property_opposite(self: uml2.Property) -> List[Optional[uml2.Property]]:
    """
    In the case where the property is one navigable end of a binary
    association with both ends navigable, this gives the other end.

    For Gaphor the property on the other end is returned regardless the
    navigability.
    """
    if self.association is not None and len(self.association.memberEnd) == 2:
        return [
            self.association.memberEnd[1]
            if self.association.memberEnd[0] is self
            else self.association.memberEnd[0]
        ]
    return [None]


uml2.Property.opposite = derived(
    uml2.Property, "opposite", uml2.Property, 0, 1, property_opposite
)


def property_navigability(self: uml2.Property) -> List[Optional[bool]]:
    """
    Get navigability of an association end.
    If no association is related to the property, then unknown navigability
    is assumed.
    """
    assoc = self.association
    if not assoc or not self.opposite:
        return [None]  # assume unknown
    owner = self.opposite.type
    if (
        isinstance(owner, (uml2.Class, uml2.Interface))
        and isinstance(self.type, (uml2.Class, uml2.Interface))
        and (self in owner.ownedAttribute)
        or self in assoc.navigableOwnedEnd
    ):
        return [True]
    elif self in assoc.ownedEnd:
        return [None]
    else:
        return [False]


uml2.Property.navigability = derived(
    uml2.Property, "navigability", bool, 0, 1, property_navigability
)


def _pr_interface_deps(classifier, dep_type):
    """
    Return all interfaces, which are connected to a classifier with given
    dependency type.
    """
    return (
        dep.supplier[0]
        for dep in classifier.clientDependency
        if dep.isKindOf(dep_type) and dep.supplier[0].isKindOf(uml2.Interface)
    )


def _pr_rc_interface_deps(component, dep_type):
    """
    Return all interfaces, which are connected to realizing classifiers of
    specified component. Returned interfaces are connected to realizing
    classifiers with given dependency type.

    Generator of generators is returned. Do not forget to flat it later.
    """
    return (
        _pr_interface_deps(r.realizingClassifier, dep_type)
        for r in component.realization
    )


def component_provided(self) -> List[Union[uml2.Implementation, uml2.Realization]]:
    """
    Interfaces provided to component environment.
    """
    implementations = (
        impl.contract[0]
        for impl in self.implementation
        if impl.isKindOf(uml2.Implementation)
    )
    realizations = _pr_interface_deps(self, uml2.Realization)

    # realizing classifiers realizations
    # this generator of generators, so flatten it later
    rc_realizations = _pr_rc_interface_deps(self, uml2.Realization)

    return list(itertools.chain(implementations, realizations, *rc_realizations))


uml2.Component.provided = property(component_provided, doc=component_provided.__doc__)


def component_required(self) -> List[uml2.Usage]:
    """
    Interfaces required by component.
    """
    usages = _pr_interface_deps(self, uml2.Usage)

    # realizing classifiers usages
    # this generator of generators, so flatten it later
    rc_usages = _pr_rc_interface_deps(self, uml2.Usage)

    return list(itertools.chain(usages, *rc_usages))


uml2.Component.required = property(component_required, doc=component_required.__doc__)


def message_messageKind(self) -> str:
    """
    MessageKind
    """
    kind = "unknown"
    if self.sendEvent:
        kind = "lost"
        if self.receiveEvent:
            kind = "complete"
    elif self.receiveEvent:
        kind = "found"
    return kind


uml2.Message.messageKind = property(
    message_messageKind, doc=message_messageKind.__doc__
)


def namedelement_qualifiedname(self) -> List[str]:
    """
    Returns the qualified name of the element as a tuple
    """
    if self.namespace:
        return namedelement_qualifiedname(self.namespace) + [self.name]
    else:
        return [self.name]


uml2.Lifeline.parse = umllex.parse_lifeline
uml2.Lifeline.render = umllex.render_lifeline

uml2.NamedElement.qualifiedName = derived(
    uml2.NamedElement,
    "qualifiedName",
    List[str],
    0,
    1,
    lambda obj: [namedelement_qualifiedname(obj)],
)
