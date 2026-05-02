import pytest

from gaphor.KerML import kerml


def test_subset_owned_annotation_from_owned_relationship(element_factory):
    element = element_factory.create(kerml.Element)
    annotation = element_factory.create(kerml.Annotation)

    element.ownedRelationship = annotation

    assert annotation in element.ownedAnnotation


@pytest.mark.xfail
def test_owning_annotation(element_factory):
    element = element_factory.create(kerml.Element)
    annotation = element_factory.create(kerml.Annotation)
    comment = element_factory.create(kerml.Comment)

    element.ownedRelationship = annotation
    comment.annotation = annotation

    assert comment in element.annotatingElement
    assert element in comment.annotatedElement
