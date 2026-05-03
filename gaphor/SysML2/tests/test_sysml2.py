from gaphor.diagram.group import Root, change_owner, owner, owns
from gaphor.KerML import kerml
from gaphor.SysML2 import sysml2


def test_ownership(element_factory):
    pkg = element_factory.create(kerml.Package)
    adef = element_factory.create(sysml2.AttributeDefinition)
    membership = element_factory.create(kerml.OwningMembership)

    pkg.ownedRelationship = membership
    adef.owningRelationship = membership

    assert adef.owner is pkg


def test_owner_function_reports_root_for_unowned_element(element_factory):
    element = element_factory.create(sysml2.PartDefinition)

    assert owner(element) is Root


def test_change_owner_assigns_owning_membership(element_factory):
    pkg = element_factory.create(kerml.Package)
    part = element_factory.create(sysml2.PartDefinition)

    assert change_owner(pkg, part)
    assert part.owner is pkg
    assert owner(part) is pkg


def test_owns_contains_reparented_element(element_factory):
    pkg = element_factory.create(kerml.Package)
    part = element_factory.create(sysml2.PartDefinition)

    assert change_owner(pkg, part)
    assert part in owns(pkg)
