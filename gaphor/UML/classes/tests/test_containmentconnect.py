"""Test connection of containment relationship."""

from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.diagram.tests.fixtures import allow, connect, disconnect
from gaphor.UML.classes import ClassItem, PackageItem
from gaphor.UML.classes.containment import ContainmentItem


def test_containment_package_glue(create):
    """Test containment glue to two package items."""
    pkg1 = create(PackageItem, UML.Package)
    containment = create(ContainmentItem)

    assert allow(containment, containment.head, pkg1)


def test_containment_package_glue_connected_on_one_end(create):
    """Test containment glue to two package items."""
    pkg1 = create(PackageItem, UML.Package)
    pkg2 = create(PackageItem, UML.Package)
    containment = create(ContainmentItem)

    connect(containment, containment.head, pkg1)

    assert allow(containment, containment.tail, pkg2)
    assert not allow(containment, containment.tail, pkg1)


def test_containment_can_not_create_cycles(create, diagram, element_factory):
    """Test containment connecting to a package and a class."""
    package = create(PackageItem, UML.Package)
    klass = create(ClassItem, UML.Class)
    klass.subject.package = package.subject
    line = create(ContainmentItem)

    connect(line, line.head, klass)

    assert not allow(line, line.tail, package)


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


def test_containment_package_class_disconnect(create, diagram, element_factory):
    """Test containment disconnecting from a package and a class."""
    parent_package = element_factory.create(UML.Package)
    diagram.element = parent_package

    package = create(PackageItem, UML.Package)
    line = create(ContainmentItem)
    klass = create(ClassItem, UML.Class)

    connect(line, line.tail, klass)
    connect(line, line.head, package)
    disconnect(line, line.head)

    assert klass.subject in parent_package.ownedElement


def test_containment_class_class(create, diagram, element_factory):
    """Test containment connecting to a package and a class."""
    parent_package = element_factory.create(UML.Package)
    container = create(ClassItem, UML.Class)
    container.subject.package = parent_package
    line = create(ContainmentItem)
    klass = create(ClassItem, UML.Class)
    klass.subject.package = parent_package

    connect(line, line.head, container)
    connect(line, line.tail, klass)

    assert diagram.connections.get_connection(line.tail).connected is klass
    assert len(container.subject.ownedElement) == 1
    assert klass.subject.owner is container.subject
    assert klass.subject in container.subject.ownedElement


def test_containment_class_class_disconnect(create, diagram, element_factory):
    """Test containment connecting to a package and a class."""
    parent_package = element_factory.create(UML.Package)
    diagram.element = parent_package

    container = create(ClassItem, UML.Class)
    line = create(ContainmentItem)
    klass = create(ClassItem, UML.Class)

    connect(line, line.head, container)
    connect(line, line.tail, klass)
    disconnect(line, line.head)

    assert klass.subject.owner is parent_package
    assert klass.subject in parent_package.ownedElement


def test_containment_reconnect_in_new_diagram(create, element_factory):
    # Most recently created containment relation wins.
    rel = create(ContainmentItem)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)

    connect(rel, rel.head, c1)
    connect(rel, rel.tail, c2)

    # Now do the same on a new diagram:
    diagram2 = element_factory.create(Diagram)
    c3 = diagram2.create(ClassItem, subject=c1.subject)
    c4 = diagram2.create(ClassItem, subject=c2.subject)
    rel2 = diagram2.create(ContainmentItem)

    connect(rel2, rel2.head, c3)
    connect(rel2, rel2.tail, c4)

    c5 = diagram2.create(ClassItem, subject=element_factory.create(UML.Class))
    connect(rel2, rel2.head, c5)

    assert c2.subject.owner is c5.subject
    assert c4.subject.owner is c5.subject
