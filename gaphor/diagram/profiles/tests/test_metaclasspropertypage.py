"""Test Metaclass Property Page."""

import pytest
from gi.repository import Gtk

from gaphor import UML
from gaphor.diagram.profiles.metaclasspropertypage import MetaclassPropertyPage


@pytest.fixture
def class_(element_factory):
    class_ = element_factory.create(UML.Class)
    class_.name = "Class"
    yield class_
    del class_


def test_name_input_field_for_normal_class(class_):
    """Test Metaclass Property Page not create for normal Class."""

    # GIVEN a Class
    # WHEN we open a new Metaclass Property Page for the Class
    editor = MetaclassPropertyPage(class_)
    page = editor.construct()

    # THEN we don't create a property page
    assert not page


def test_name_selection_for_metaclass(element_factory, class_):
    """Test the creation of Metaclass Property Page."""

    # GIVEN a Class with a Metaclass Extension
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "NewStereotype"
    UML.model.create_extension(class_, stereotype)

    # WHEN we open a new Metaclass Property Page
    editor = MetaclassPropertyPage(class_)
    page = editor.construct()

    # THEN we create a property page
    assert page

    # WHEN we create a property page
    combo = page.get_children()[1]

    # THEN the child is a Gtk ComboBox and its child has text "Class"
    assert type(combo) is Gtk.ComboBoxText
    assert combo.get_child().get_text() == "Class"

    # WHEN we change the metaclass name
    class_.name = "Blah"

    # THEN we also update the ComboBox child's text
    assert combo.get_child().get_text() == "Blah"
