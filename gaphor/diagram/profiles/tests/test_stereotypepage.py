"""Test Stereotype Property Page."""

import pytest

from gaphor import UML
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.profiles.stereotypepropertypages import StereotypePage


@pytest.fixture
def class_(diagram, element_factory):
    class_ = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    class_.name = "Class"
    yield class_
    del class_


def test_stereotype_page_with_no_stereotype(diagram, class_):
    """Test the Stereotype Property Page not created for a Class."""

    # GIVEN a Class
    # WHEN we open a Stereotype Property Page for the Class
    editor = StereotypePage(class_)
    page = editor.construct()

    # THEN we don't create a property page
    assert page is None


def test_stereotype_page_with_stereotype(element_factory, diagram, class_):
    """Test creation of a Stereotype Property Page."""

    # Create a stereotype applicable to Class types:
    # GIVEN a Class with a MetaClass Extension, a Property, and a Class
    metaclass = element_factory.create(UML.Class)
    metaclass.name = "Class"
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "NewStereotype"
    UML.model.create_extension(metaclass, stereotype)
    attr = element_factory.create(UML.Property)
    attr.name = "Property"

    # WHEN we open a new Stereotype Property Page
    editor = StereotypePage(class_)
    page = editor.construct()
    editor.refresh()

    # THEN we create an editor model, and a property page
    assert len(editor.model) == 1
    assert page is not None
