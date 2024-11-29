from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.profiles.stereotypepropertypages import (
    ShowStereotypePage,
    StereotypePage,
)


def create_property_page(diagram, element_factory, event_manager) -> StereotypePage:
    return StereotypePage(element_factory.create(UML.Class), event_manager)


def create_show_property_page(
    diagram, element_factory, event_manager
) -> ShowStereotypePage:
    item = diagram.create(
        UML.classes.ClassItem, subject=element_factory.create(UML.Class)
    )
    return ShowStereotypePage(item, event_manager)


def get_model(property_page: StereotypePage):
    widget = property_page.construct()
    show_stereotypes = find(widget, "stereotype-list")
    return show_stereotypes.get_model()


def metaclass_and_stereotype(element_factory):
    metaclass = element_factory.create(UML.Class)
    metaclass.name = "Class"
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "Stereotype"
    UML.recipes.create_extension(metaclass, stereotype)
    return metaclass, stereotype


def test_show_stereotype_property_page_with_stereotype(
    diagram, element_factory, event_manager
):
    _metaclass, _stereotype = metaclass_and_stereotype(element_factory)
    property_page = create_show_property_page(diagram, element_factory, event_manager)

    widget = property_page.construct()
    show_stereotypes = find(widget, "show-stereotypes")
    show_stereotypes.set_active(True)

    assert property_page.item.show_stereotypes


def test_stereotype_property_page_apply_stereotype(
    diagram, element_factory, event_manager
):
    _metaclass, stereotype = metaclass_and_stereotype(element_factory)

    property_page = create_property_page(diagram, element_factory, event_manager)
    subject = property_page.subject
    model = get_model(property_page)
    view = model[0]
    view.applied = True

    assert stereotype in subject.appliedStereotype[0].classifier


def test_stereotype_property_page_slot_value(diagram, element_factory, event_manager):
    metaclass = element_factory.create(UML.Class)
    metaclass.name = "Class"
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "Stereotype"
    stereotype.ownedAttribute = element_factory.create(UML.Property)
    UML.recipes.create_extension(metaclass, stereotype)

    property_page = create_property_page(diagram, element_factory, event_manager)
    model = get_model(property_page)
    model[0].applied = True
    model[1].slot_value = "test"
    applied_stereotype = property_page.subject.appliedStereotype[0]
    slot = applied_stereotype.slot[0]

    assert stereotype.ownedAttribute[0] is slot.definingFeature
    assert "test" == slot.value


def test_inherited_stereotype(diagram, element_factory, event_manager):
    _metaclass, stereotype = metaclass_and_stereotype(element_factory)
    substereotype = element_factory.create(UML.Stereotype)
    substereotype.name = "SubStereotype"
    UML.recipes.create_generalization(stereotype, substereotype)

    property_page = create_property_page(diagram, element_factory, event_manager)
    model = get_model(property_page)

    assert model[0]
    assert model[0].name == "Stereotype"
    assert model[1]
    assert model[1].name == "SubStereotype"


def test_inherited_stereotype_with_attributes(diagram, element_factory, event_manager):
    _metaclass, stereotype = metaclass_and_stereotype(element_factory)
    attr = element_factory.create(UML.Property)
    attr.name = "Attr"
    stereotype.ownedAttribute = attr
    substereotype = element_factory.create(UML.Stereotype)
    substereotype.name = "SubStereotype"
    UML.recipes.create_generalization(stereotype, substereotype)

    property_page = create_property_page(diagram, element_factory, event_manager)
    model = get_model(property_page)

    assert model[0]
    assert model[0].name == "Stereotype"
    assert model[1].name == "Attr"
    assert model[2]
    assert model[2].name == "SubStereotype"
    assert model[3].name == "Attr"
