from gaphor.KerML import kerml
from gaphor.SysML2 import sysml2


def test_ownership(element_factory):
    pkg = element_factory.create(kerml.Package)
    adef = element_factory.create(sysml2.AttributeDefinition)
    membership = element_factory.create(kerml.OwningMembership)

    pkg.ownedRelationship = membership
    adef.owningRelationship = membership

    assert adef.owner is pkg
