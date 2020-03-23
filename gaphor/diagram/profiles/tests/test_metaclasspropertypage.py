"""Test Metaclass Property Page."""

from gi.repository import Gtk

from gaphor import UML
from gaphor.diagram.profiles.metaclasspropertypage import MetaclassPropertyPage


def test_name_input_field_for_normal_class(element_factory):
    class_ = element_factory.create(UML.Class)
    class_.name = "Class"
    editor = MetaclassPropertyPage(class_)
    page = editor.construct()
    assert not page


def test_name_selection_for_metaclass(element_factory):
    metaclass = element_factory.create(UML.Class)
    metaclass.name = "Class"
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "NewStereotype"
    UML.model.create_extension(metaclass, stereotype)

    editor = MetaclassPropertyPage(metaclass)
    page = editor.construct()
    assert page
    combo = page.get_children()[1]
    assert Gtk.ComboBoxText is type(combo)

    assert "Class" == combo.get_child().get_text()

    metaclass.name = "Blah"
    assert "Blah" == combo.get_child().get_text()
