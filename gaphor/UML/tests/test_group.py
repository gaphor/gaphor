from gaphor.diagram.group import can_group, group, ungroup
from gaphor.UML.uml import Activity, Class, Package


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


def test_group_package_and_package(element_factory):
    package = element_factory.create(Package)
    parent = element_factory.create(Package)

    assert group(parent, package)

    assert package.owner is parent


def test_ungroup_package(element_factory):
    package = element_factory.create(Package)
    parent = element_factory.create(Package)
    group(parent, package)

    assert ungroup(parent, package)

    assert package.package is None


def test_do_not_ungroup_package_wrong_parent(element_factory):
    package = element_factory.create(Package)
    parent = element_factory.create(Package)
    wrong_parent = element_factory.create(Package)
    group(parent, package)

    assert not ungroup(wrong_parent, package)

    assert package.package is parent


def test_group_class_and_activity(element_factory):
    klass = element_factory.create(Class)
    activity = element_factory.create(Activity)

    assert group(klass, activity)

    assert activity.owner is klass


def test_group_class_and_activity_from_package(element_factory):
    klass = element_factory.create(Class)
    activity = element_factory.create(Activity)

    assert group(klass, activity)

    assert activity.owner is klass


def test_ungroup_class_and_activity(element_factory):
    package = element_factory.create(Package)
    klass = element_factory.create(Class)
    activity = element_factory.create(Activity)

    group(package, activity)
    group(klass, activity)

    assert activity.owner is klass
