from gi.repository import Gtk

from gaphor import UML
from gaphor.diagram.classes.classespropertypages import ClassPropertyPage
from gaphor.tests import TestCase


class MetaclassPropertyPageTest(TestCase):
    def test_name_input_field_for_normal_class(self):
        class_ = self.element_factory.create(UML.Class)

        class_.name = "Class"
        editor = ClassPropertyPage(class_)
        page = editor.construct()
        assert page
        entry = page.get_children()[0].get_children()[1]
        assert Gtk.Entry is type(entry)

        assert "Class" == entry.get_text()

        class_.name = "Blah"
        assert "Blah" == entry.get_text()

    def test_name_selection_for_metaclass(self):
        metaclass = self.element_factory.create(UML.Class)
        metaclass.name = "Class"
        stereotype = self.element_factory.create(UML.Stereotype)
        stereotype.name = "NewStereotype"
        UML.model.create_extension(metaclass, stereotype)

        editor = ClassPropertyPage(metaclass)
        page = editor.construct()
        assert page
        combo = page.get_children()[0].get_children()[1]
        assert Gtk.ComboBox is type(combo)

        assert "Class" == combo.get_child().get_text()

        metaclass.name = "Blah"
        assert "Blah" == combo.get_child().get_text()
