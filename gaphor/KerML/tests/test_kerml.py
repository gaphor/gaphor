from gaphor.KerML import kerml


def test_subset_owned_annotation_from_owned_relationship(element_factory):
    element = element_factory.create(kerml.Element)
    annotation = element_factory.create(kerml.Annotation)

    element.ownedRelationship = annotation

    assert annotation in element.ownedAnnotation
