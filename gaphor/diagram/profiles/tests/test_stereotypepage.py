"""Test Stereotype Property Page."""

from gaphor import UML
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.profiles.stereotypepropertypages import StereotypePage


def test_stereotype_page_with_no_stereotype(element_factory, diagram):
    ci = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    ci.subject.name = "Class"
    editor = StereotypePage(ci)
    page = editor.construct()
    assert page is None


def test_stereotype_page_with_stereotype(element_factory, diagram):
    # Create a stereotype applicable to Class types:
    metaclass = element_factory.create(UML.Class)
    metaclass.name = "Class"
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "NewStereotype"
    UML.model.create_extension(metaclass, stereotype)
    attr = element_factory.create(UML.Property)
    attr.name = "Property"
    # stereotype.ownedAttribute = attr

    ci = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    ci.subject.name = "Foo"
    editor = StereotypePage(ci)
    page = editor.construct()

    editor.refresh()
    assert len(editor.model) == 1
    assert page is not None
