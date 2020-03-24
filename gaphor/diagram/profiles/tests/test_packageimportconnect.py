"""Package Import Item connection adapter tests."""

from gaphor import UML
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.classes.package import PackageItem
from gaphor.diagram.profiles.packageimport import PackageImportItem
from gaphor.diagram.tests.fixtures import allow, connect


def test_glue(element_factory, diagram):
    """Test gluing package import item."""

    # GIVEN a package import relationship and two packages
    pkg_import = diagram.create(PackageImportItem)
    package1 = diagram.create(PackageItem, subject=element_factory.create(UML.Package))
    package2 = diagram.create(PackageItem, subject=element_factory.create(UML.Package))
    # WHEN the package import tail is attached to package1
    glued = allow(pkg_import, pkg_import.tail, package1)
    # THEN package1 is allowed to be glued to the relationship
    assert glued
    # GIVEN package1 is connected to the relationship
    connect(pkg_import, pkg_import.tail, package1)
    # WHEN the package import head is attached to package2
    glued = allow(pkg_import, pkg_import.head, package2)
    # THEN package2 is allowed to be glued to the relationship
    assert glued


def test_package_glue(element_factory, diagram):
    """Test package import item can't glue to a class."""

    # GIVEN a package import relationship and a class
    pkg_import = diagram.create(PackageImportItem)
    import_class = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    # WHEN the package import relationship is attached to the class
    glued = allow(pkg_import, pkg_import.head, import_class)
    # THEN the class is not glued to the relationship
    assert not glued


def test_connection(element_factory, diagram):
    """Test package import item connection."""

    # GIVEN a package import relationship and two packages
    pkg_import = diagram.create(PackageImportItem)
    package1 = diagram.create(PackageItem, subject=element_factory.create(UML.Package))
    package2 = diagram.create(PackageItem, subject=element_factory.create(UML.Package))
    # WHEN connecting the package import relationship to both packages
    # THEN the connection is successful
    connect(pkg_import, pkg_import.tail, package1)
    connect(pkg_import, pkg_import.head, package2)
