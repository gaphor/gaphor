from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.profiles.stereotypepropertypages import (
    StereotypePage,
    set_value,
    toggle_stereotype,
)


def create_property_page(diagram, element_factory) -> StereotypePage:
    item = diagram.create(
        UML.classes.ClassItem, subject=element_factory.create(UML.Class)
    )
    return StereotypePage(item)


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


def test_stereotype_property_page_with_stereotype(diagram, element_factory):
    metaclass, stereotype = metaclass_and_stereotype(element_factory)
    property_page = create_property_page(diagram, element_factory)

    widget = property_page.construct()
    show_stereotypes = find(widget, "show-stereotypes")
    show_stereotypes.set_active(True)

    assert property_page.item.show_stereotypes


def test_stereotype_property_page_apply_stereotype(diagram, element_factory):
    _metaclass, stereotype = metaclass_and_stereotype(element_factory)

    property_page = create_property_page(diagram, element_factory)
    item = property_page.item
    model = get_model(property_page)
    toggle_stereotype(None, (0,), item.subject, model)

    assert stereotype in item.subject.appliedStereotype[0].classifier


def test_stereotype_property_page_slot_value(diagram, element_factory):
    metaclass = element_factory.create(UML.Class)
    metaclass.name = "Class"
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "Stereotype"
    stereotype.ownedAttribute = element_factory.create(UML.Property)
    UML.recipes.create_extension(metaclass, stereotype)

    property_page = create_property_page(diagram, element_factory)
    item = property_page.item
    model = get_model(property_page)
    toggle_stereotype(None, (0,), item.subject, model)
    set_value(None, (0, 0), "test", model)
    slot = item.subject.appliedStereotype[0].slot[0]

    assert stereotype.ownedAttribute[0] is slot.definingFeature
    assert "test" == slot.value


def test_inherited_stereotype(diagram, element_factory):
    metaclass, stereotype = metaclass_and_stereotype(element_factory)
    substereotype = element_factory.create(UML.Stereotype)
    substereotype.name = "SubStereotype"
    UML.recipes.create_generalization(stereotype, substereotype)

    property_page = create_property_page(diagram, element_factory)
    model = get_model(property_page)

    assert model[(0,)]
    assert model[(0,)][0] == "Stereotype"
    assert model[(1,)]
    assert model[(1,)][0] == "SubStereotype"


def test_inherited_stereotype_with_attributes(diagram, element_factory):
    metaclass, stereotype = metaclass_and_stereotype(element_factory)
    attr = element_factory.create(UML.Property)
    attr.name = "Attr"
    stereotype.ownedAttribute = attr
    substereotype = element_factory.create(UML.Stereotype)
    substereotype.name = "SubStereotype"
    UML.recipes.create_generalization(stereotype, substereotype)

    property_page = create_property_page(diagram, element_factory)
    model = get_model(property_page)

    assert model[(0,)]
    assert model[(0,)][0] == "Stereotype"
    assert model[(0, 0)][0] == "Attr"
    assert model[(1,)]
    assert model[(1,)][0] == "SubStereotype"
    assert model[(1, 0)][0] == "Attr"
