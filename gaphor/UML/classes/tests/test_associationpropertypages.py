from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.classes.associationpropertypages import AssociationPropertyPage


def test_association_property_page(diagram, element_factory):
    end1 = element_factory.create(UML.Class)
    end2 = element_factory.create(UML.Class)
    item = diagram.create(
        UML.classes.AssociationItem, subject=UML.recipes.create_association(end1, end2)
    )
    item.head_subject = item.subject.memberEnd[0]
    item.tail_subject = item.subject.memberEnd[1]
    property_page = AssociationPropertyPage(item)

    widget = property_page.construct()
    head_name = find(widget, "head-name")
    head_name.set_text("head")

    assert item.subject.memberEnd[0].name == "head"


def test_association_property_page_with_no_subject(diagram, element_factory):
    item = diagram.create(UML.classes.AssociationItem)
    property_page = AssociationPropertyPage(item)

    widget = property_page.construct()

    assert widget is None


def test_association_property_page_invert_direction(diagram, element_factory):
    end1 = element_factory.create(UML.Class)
    end2 = element_factory.create(UML.Class)
    item = diagram.create(
        UML.classes.AssociationItem, subject=UML.recipes.create_association(end1, end2)
    )
    item.head_subject = item.subject.memberEnd[0]
    item.tail_subject = item.subject.memberEnd[1]
    property_page = AssociationPropertyPage(item)

    property_page._on_invert_direction_change(None)

    assert item.tail_subject is item.subject.memberEnd[0]
