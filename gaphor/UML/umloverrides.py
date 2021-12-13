"""Special methods (overrides) that add behavior to the model that cannot
simply be generated.

Derived methods always return a list. Note this is not the case for
normal properties.
"""

from __future__ import annotations

import itertools

from gaphor.core.modeling.properties import derived
from gaphor.UML import uml, umllex


# See https://www.omg.org/spec/UML/2.5/PDF, section 12.4.1.5, page 271
def extension_metaclass(self):
    """References the Class that is extended through an Extension.

    The property is derived from the type of the memberEnd that is not
    the ownedEnd.
    """
    ownedEnd = self.ownedEnd
    metaend = [e for e in self.memberEnd if e is not ownedEnd]
    if metaend:
        return metaend[0].type


# Don't use derived() now, it can not deal with a [0..1] property derived from a [0..*] property.
# Extension.metaclass = derived(Extension, 'metaclass', Class, 0, 1, Extension.ownedEnd, Association.memberEnd)  # noqa: E800
# Extension.metaclass.filter = extension_metaclass  # noqa: E800
uml.Extension.metaclass = property(extension_metaclass, doc=extension_metaclass.__doc__)


def property_opposite(self: uml.Property) -> list[uml.Property | None]:
    """In the case where the property is one navigable end of a binary
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


uml.Property.opposite = derived("opposite", uml.Property, 0, 1, property_opposite)


def property_navigability(self: uml.Property) -> list[bool | None]:
    """Get navigability of an association end.

    If no association is related to the property, then unknown
    navigability is assumed.
    """
    assoc = self.association
    if not (assoc and self.opposite):
        return [None]  # assume unknown
    owner = self.opposite.type
    if (
        isinstance(owner, (uml.Class, uml.DataType, uml.Interface))
        and isinstance(self.type, (uml.Class, uml.DataType, uml.Interface))
        and (self in owner.ownedAttribute)
        or self in assoc.navigableOwnedEnd
    ):
        return [True]
    elif isinstance(assoc.ownedEnd, uml.ExtensionEnd):
        return [self is assoc.ownedEnd]
    elif assoc.ownedEnd is None or self in assoc.ownedEnd:
        return [None]
    else:
        return [False]


uml.Property.navigability = derived("navigability", bool, 0, 1, property_navigability)


def _pr_interface_deps(classifier, dep_type):
    """Return all interfaces, which are connected to a classifier with given
    dependency type."""
    return (
        dep.supplier[0]
        for dep in classifier.clientDependency
        if dep.isKindOf(dep_type) and dep.supplier[0].isKindOf(uml.Interface)
    )


def _pr_rc_interface_deps(component, dep_type):
    """Return all interfaces, which are connected to realizing classifiers of
    specified component. Returned interfaces are connected to realizing
    classifiers with given dependency type.

    Generator of generators is returned. Do not forget to flat it later.
    """
    return (
        _pr_interface_deps(r.realizingClassifier, dep_type)
        for r in component.realization
    )


def component_provided(self) -> list[uml.Realization]:
    """Interfaces provided to component environment."""
    implementations = (
        impl.contract[0]
        for impl in self.interfaceRealization
        if impl.isKindOf(uml.InterfaceRealization)
    )
    realizations = _pr_interface_deps(self, uml.Realization)

    # realizing classifiers realizations
    # this generator of generators, so flatten it later
    rc_realizations = _pr_rc_interface_deps(self, uml.Realization)

    return list(itertools.chain(implementations, realizations, *rc_realizations))


uml.Component.provided = property(component_provided, doc=component_provided.__doc__)


def component_required(self) -> list[uml.Usage]:
    """Interfaces required by component."""
    usages = _pr_interface_deps(self, uml.Usage)

    # realizing classifiers usages
    # this generator of generators, so flatten it later
    rc_usages = _pr_rc_interface_deps(self, uml.Usage)

    return list(itertools.chain(usages, *rc_usages))


uml.Component.required = property(component_required, doc=component_required.__doc__)


def message_messageKind(self) -> str:
    """MessageKind."""
    kind = "unknown"
    if self.sendEvent:
        kind = "complete" if self.receiveEvent else "lost"
    elif self.receiveEvent:
        kind = "found"
    return kind


uml.Message.messageKind = property(message_messageKind, doc=message_messageKind.__doc__)


uml.Lifeline.parse = umllex.parse_lifeline
uml.Lifeline.render = umllex.render_lifeline
