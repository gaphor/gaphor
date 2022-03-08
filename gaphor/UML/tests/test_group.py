from gaphor.diagram.group import can_group, group, ungroup
from gaphor.UML.uml import Class, Package


def test_can_group_package_and_class(element_factory):
    package = element_factory.create(Package)
    klass = element_factory.create(Class)

    assert can_group(package, klass)


def test_group_package_and_class(element_factory):
    package = element_factory.create(Package)
    klass = element_factory.create(Class)

    assert group(package, klass)

    assert klass.owner is package


def test_ungroup(element_factory):
    package = element_factory.create(Package)
    klass = element_factory.create(Class)
    group(package, klass)

    assert ungroup(package, klass)

    assert klass.package is None


def test_do_not_ungroup_wrong_parent(element_factory):
    package = element_factory.create(Package)
    klass = element_factory.create(Class)
    wrong_package = element_factory.create(Package)
    group(package, klass)

    assert not ungroup(wrong_package, klass)

    assert klass.package is package
