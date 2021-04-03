"""Test connection of containment relationship."""

from gaphor import UML
from gaphor.diagram.tests.fixtures import allow, connect
from gaphor.UML.classes import ClassItem, PackageItem
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


def test_containment_package_class(create, diagram):
    """Test containment connecting to a package and a class."""
    package = create(ContainmentItem, UML.Package)
    line = create(ContainmentItem)
    ac = create(ClassItem, UML.Class)

    connect(line, line.head, package)
    connect(line, line.tail, ac)
    assert diagram.connections.get_connection(line.tail).connected is ac
    assert len(package.subject.ownedElement) == 1
    assert ac.subject in package.subject.ownedElement
