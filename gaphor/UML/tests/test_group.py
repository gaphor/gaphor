import pytest

import gaphor.UML.uml as UML
from gaphor.diagram.group import can_group, group, owner, ungroup
from gaphor.UML.recipes import create_association, set_navigability


def test_can_group_package_and_class(element_factory):
    package = element_factory.create(UML.Package)
    klass = element_factory.create(UML.Class)

    assert can_group(package, klass)


def test_group_package_and_class(element_factory):
    package = element_factory.create(UML.Package)
    klass = element_factory.create(UML.Class)

    assert group(package, klass)

    assert klass.owner is package


def test_ungroup(element_factory):
    package = element_factory.create(UML.Package)
    klass = element_factory.create(UML.Class)
    group(package, klass)

    assert ungroup(package, klass)

    assert klass.package is None


def test_do_not_ungroup_wrong_parent(element_factory):
    package = element_factory.create(UML.Package)
    klass = element_factory.create(UML.Class)
    wrong_package = element_factory.create(UML.Package)
    group(package, klass)

    assert not ungroup(wrong_package, klass)

    assert klass.package is package


def test_group_package_and_package(element_factory):
    package = element_factory.create(UML.Package)
    parent = element_factory.create(UML.Package)

    assert group(parent, package)

    assert package.owner is parent


def test_ungroup_package(element_factory):
    package = element_factory.create(UML.Package)
    parent = element_factory.create(UML.Package)
    group(parent, package)

    assert ungroup(parent, package)

    assert package.nestingPackage is None


def test_do_not_ungroup_package_wrong_parent(element_factory):
    package = element_factory.create(UML.Package)
    parent = element_factory.create(UML.Package)
    wrong_parent = element_factory.create(UML.Package)
    group(parent, package)

    assert not ungroup(wrong_parent, package)

    assert package.nestingPackage is parent


def test_group_class_and_activity(element_factory):
    klass = element_factory.create(UML.Class)
    activity = element_factory.create(UML.Activity)

    assert group(klass, activity)

    assert activity.owner is klass


def test_group_class_and_activity_from_package(element_factory):
    klass = element_factory.create(UML.Class)
    activity = element_factory.create(UML.Activity)

    assert group(klass, activity)

    assert activity.owner is klass


def test_ungroup_class_and_activity(element_factory):
    package = element_factory.create(UML.Package)
    klass = element_factory.create(UML.Class)
    activity = element_factory.create(UML.Activity)

    group(package, activity)
    group(klass, activity)

    assert activity.owner is klass


@pytest.mark.parametrize(
    "classifier_type,feature_type",
    [
        (UML.Artifact, UML.Operation),
        (UML.Class, UML.Operation),
        (UML.DataType, UML.Operation),
        (UML.Interface, UML.Operation),
        (UML.Artifact, UML.Property),
        (UML.Class, UML.Property),
        (UML.DataType, UML.Property),
        (UML.Interface, UML.Property),
    ],
)
def test_group_classifier_and_feature(classifier_type, feature_type, element_factory):
    classifier = element_factory.create(classifier_type)
    feature = element_factory.create(feature_type)
    classifier2 = element_factory.create(classifier_type)

    assert group(classifier, feature)
    assert group(classifier2, feature)

    assert feature.owner is classifier2


def test_should_not_group_association_end(element_factory):
    head_class = element_factory.create(UML.Class)
    tail_class = element_factory.create(UML.Class)
    association = create_association(head_class, tail_class)
    set_navigability(association, association.memberEnd[0], True)
    other_class = element_factory.create(UML.Class)
    end = association.memberEnd[0]

    assert not group(other_class, end)
    assert not ungroup(end.owner, end)


@pytest.mark.parametrize(
    "element_type",
    [
        UML.Slot,
        UML.Comment,
        UML.Image,
        UML.InstanceSpecification,
        UML.OccurrenceSpecification,
        UML.LiteralSpecification,
        UML.LiteralUnlimitedNatural,
        # The following elements are not shown if they have no owner
        UML.ConnectorEnd,
        UML.Parameter,
        UML.Pin,
        UML.Property,
        UML.StructuralFeature,
    ],
)
def test_element_with_no_owner(element_type):
    assert owner(element_type()) is None
