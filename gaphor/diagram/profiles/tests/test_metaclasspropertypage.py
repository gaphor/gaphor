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

    editor = MetaclassPropertyPage(class_)
    page = editor.construct()

    assert not page


def test_name_selection_for_metaclass(element_factory, class_):
    """Test the creation of Metaclass Property Page."""

    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "NewStereotype"
    UML.model.create_extension(class_, stereotype)

    editor = MetaclassPropertyPage(class_)
    page = editor.construct()

    assert page

    combo = page.get_children()[1]

    assert type(combo) is Gtk.ComboBoxText
    assert combo.get_child().get_text() == "Class"

    class_.name = "Blah"

    assert combo.get_child().get_text() == "Blah"
