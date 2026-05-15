from gaphor.diagram.group import Root, group, owner, owns, ungroup
from gaphor.KerML import kerml


@owner.register
def _(element: kerml.Element):
    return element.owner or Root


@owns.register
def _(element: kerml.Element):
    return [e for e in element.ownedElement if e.owner is element and owner(e)]


@group.register(kerml.Namespace, kerml.Element)
def namespace_group(parent: kerml.Namespace, element: kerml.Element) -> bool:
    if element.owner:
        ungroup(element.owner, element)

    membership = element.model.create(kerml.OwningMembership)
    membership.owningRelatedElement = parent
    membership.ownedRelatedElement = element
    return True


@ungroup.register(kerml.Namespace, kerml.Element)
def namespace_ungroup(parent: kerml.Namespace, element: kerml.Element) -> bool:
    membership = element.owningMembership
    if membership and membership.membershipOwningNamespace is parent:
        membership.unlink()
        return True
    return False
