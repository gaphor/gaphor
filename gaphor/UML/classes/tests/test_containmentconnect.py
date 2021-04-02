"""Test connection of containment relationship."""

from gaphor import UML
from gaphor.diagram.tests.fixtures import allow, connect
from gaphor.UML.classes import PackageItem
from gaphor.UML.classes.containment import ContainmentItem


def test_containment_package_glue(create):
    """Test containment glue to two package items."""
    pkg1 = create(PackageItem, UML.Package)
    pkg2 = create(PackageItem, UML.Package)
    containment = create(ContainmentItem)

    glued = allow(containment, containment.head, pkg1)
    assert glued

    connect(containment, containment.head, pkg1)

    glued = allow(containment, containment.tail, pkg2)
    assert glued
