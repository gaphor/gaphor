"""Test connection of containment relationship."""

from gaphor import UML
from gaphor.diagram.tests.fixtures import allow, connect, disconnect
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
    package = create(PackageItem, UML.Package)
    line = create(ContainmentItem)
    klass = create(ClassItem, UML.Class)

    connect(line, line.head, package)
    connect(line, line.tail, klass)
    assert diagram.connections.get_connection(line.tail).connected is klass
    assert len(package.subject.ownedElement) == 1
    assert klass.subject in package.subject.ownedElement


def test_disconnect_containment_package_class(create, diagram, element_factory):
    """Test containment connecting to a package and a class."""
    parent_package = element_factory.create(UML.Package)
    diagram.package = parent_package

    package = create(PackageItem, UML.Package)
    line = create(ContainmentItem)
    klass = create(ClassItem, UML.Class)

    connect(line, line.tail, klass)
    connect(line, line.head, package)
    disconnect(line, line.head)

    assert klass.subject in parent_package.ownedElement
