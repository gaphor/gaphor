from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.classes.associationpropertypages import (
    AssociationDirectionPropertyPage,
    AssociationPropertyPage,
)


def test_association_property_page(element_factory, event_manager):
    end1 = element_factory.create(UML.Class)
    end2 = element_factory.create(UML.Class)
    subject = UML.recipes.create_association(end1, end2)

    property_page = AssociationPropertyPage(subject, event_manager)

    widget = property_page.construct()
    head_name = find(widget, "head-name")
    head_name.set_text("head")

    assert subject.memberEnd[0].name == "head"


def test_association_property_page_invert_direction(
    diagram, element_factory, event_manager
):
    end1 = element_factory.create(UML.Class)
    end2 = element_factory.create(UML.Class)
    item = diagram.create(
        UML.classes.AssociationItem, subject=UML.recipes.create_association(end1, end2)
    )
    item.head_subject = item.subject.memberEnd[0]
    item.tail_subject = item.subject.memberEnd[1]
    property_page = AssociationDirectionPropertyPage(item, event_manager)

    property_page.on_invert_direction_change(None)

    assert item.tail_subject is item.subject.memberEnd[0]


def metaclass_and_stereotype(element_factory):
    metaclass = element_factory.create(UML.Class)
    metaclass.name = "Element"
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "Stereotype"
    UML.recipes.create_extension(metaclass, stereotype)
    return metaclass, stereotype


def test_association_property_with_stereotype(element_factory, event_manager):
    end1 = element_factory.create(UML.Class)
    end2 = element_factory.create(UML.Class)
    subject = UML.recipes.create_association(end1, end2)
    metaclass_and_stereotype(element_factory)

    property_page = AssociationPropertyPage(subject, event_manager)

    widget = property_page.construct()

    assert widget
