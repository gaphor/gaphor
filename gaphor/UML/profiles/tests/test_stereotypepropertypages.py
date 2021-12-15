from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.profiles.stereotypepropertypages import (
    StereotypePage,
    set_value,
    toggle_stereotype,
)


def test_stereotype_property_page_without_stereotype(diagram, element_factory):
    item = diagram.create(
        UML.classes.ClassItem, subject=element_factory.create(UML.Class)
    )
    property_page = StereotypePage(item)

    widget = property_page.construct()

    assert widget is None


def test_stereotype_property_page_with_stereotype(diagram, element_factory):
    metaclass = element_factory.create(UML.Class)
    metaclass.name = "Class"
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "Stereotype"
    UML.recipes.create_extension(metaclass, stereotype)

    item = diagram.create(
        UML.classes.ClassItem, subject=element_factory.create(UML.Class)
    )
    property_page = StereotypePage(item)

    widget = property_page.construct()
    show_stereotypes = find(widget, "show-stereotypes")
    show_stereotypes.set_active(True)

    assert item.show_stereotypes


def test_stereotype_property_page_apply_stereotype(diagram, element_factory):
    metaclass = element_factory.create(UML.Class)
    metaclass.name = "Class"
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "Stereotype"
    UML.recipes.create_extension(metaclass, stereotype)

    item = diagram.create(
        UML.classes.ClassItem, subject=element_factory.create(UML.Class)
    )
    property_page = StereotypePage(item)

    widget = property_page.construct()
    show_stereotypes = find(widget, "stereotype-list")
    model = show_stereotypes.get_model()
    toggle_stereotype(None, (0,), item.subject, model)

    assert stereotype in item.subject.appliedStereotype[0].classifier


def test_stereotype_property_page_slot_value(diagram, element_factory):
    metaclass = element_factory.create(UML.Class)
    metaclass.name = "Class"
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "Stereotype"
    stereotype.ownedAttribute = element_factory.create(UML.Property)
    UML.recipes.create_extension(metaclass, stereotype)

    item = diagram.create(
        UML.classes.ClassItem, subject=element_factory.create(UML.Class)
    )
    property_page = StereotypePage(item)

    widget = property_page.construct()
    show_stereotypes = find(widget, "stereotype-list")
    model = show_stereotypes.get_model()
    toggle_stereotype(None, (0,), item.subject, model)
    set_value(None, (0, 0), "test", model)
    slot = item.subject.appliedStereotype[0].slot[0]

    assert stereotype.ownedAttribute[0] is slot.definingFeature
    assert "test" == slot.value
