from gaphor.diagram.group import change_owner
from gaphor.KerML import kerml


def test_subset_owned_annotation_from_owned_relationship(element_factory):
    element = element_factory.create(kerml.Element)
    annotation = element_factory.create(kerml.Annotation)

    element.ownedRelationship = annotation

    assert annotation in element.ownedAnnotation


def test_subset_owned_annotation_removed_when_relationship_removed(element_factory):
    element = element_factory.create(kerml.Element)
    annotation = element_factory.create(kerml.Annotation)

    element.ownedRelationship = annotation
    assert annotation in element.ownedAnnotation

    annotation.unlink()

    assert annotation not in element.ownedAnnotation


def test_subset_owning_membership_tracks_owning_relationship(element_factory):
    parent = element_factory.create(kerml.Package)
    child = element_factory.create(kerml.Element)

    assert change_owner(parent, child)

    membership = child.owningMembership
    assert membership is not None
    assert child.owningRelationship is membership
    assert membership in parent.ownedRelationship
    assert child in membership.ownedRelatedElement
    assert child.owner is parent


def test_subset_owned_element_updates_on_reparent(element_factory):
    parent_1 = element_factory.create(kerml.Package)
    parent_2 = element_factory.create(kerml.Package)
    child = element_factory.create(kerml.Element)

    assert change_owner(parent_1, child)
    assert child in parent_1.ownedElement

    assert change_owner(parent_2, child)

    assert child not in parent_1.ownedElement
    assert child in parent_2.ownedElement


def test_owning_annotation(element_factory):
    element = element_factory.create(kerml.Element)
    annotation = element_factory.create(kerml.Annotation)
    comment = element_factory.create(kerml.Comment)

    element.ownedRelationship = annotation
    annotation.annotatedElement = element
    annotation.annotatingElement = comment

    assert annotation in element.ownedAnnotation
    assert element in annotation.annotatedElement
    assert comment in annotation.annotatingElement
