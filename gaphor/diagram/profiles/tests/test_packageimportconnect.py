"""Package Import Item connection adapter tests."""

from gaphor import UML
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.classes.package import PackageItem
from gaphor.diagram.profiles.packageimport import PackageImportItem
from gaphor.diagram.tests.fixtures import allow, connect


def test_glue(element_factory, diagram):
    """Test gluing package import item."""

    pkg_import = diagram.create(PackageImportItem)
    package1 = diagram.create(PackageItem, subject=element_factory.create(UML.Package))
    package2 = diagram.create(PackageItem, subject=element_factory.create(UML.Package))

    glued = allow(pkg_import, pkg_import.tail, package1)

    assert glued

    connect(pkg_import, pkg_import.tail, package1)

    glued = allow(pkg_import, pkg_import.head, package2)

    assert glued


def test_package_glue(element_factory, diagram):
    """Test package import item can't glue to a class."""

    pkg_import = diagram.create(PackageImportItem)
    import_class = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    glued = allow(pkg_import, pkg_import.head, import_class)

    assert not glued


def test_connection(element_factory, diagram):
    """Test package import item connection."""

    pkg_import = diagram.create(PackageImportItem)
    package1 = diagram.create(PackageItem, subject=element_factory.create(UML.Package))
    package2 = diagram.create(PackageItem, subject=element_factory.create(UML.Package))

    connect(pkg_import, pkg_import.tail, package1)
    connect(pkg_import, pkg_import.head, package2)
