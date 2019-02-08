from gaphor.tests import TestCase
from gaphor.adapters.profiles.stereotypepage import StereotypePage
from gaphor.diagram import items
from gaphor import UML
from gi.repository import Gtk


class MetaclassEditorTest(TestCase):

    def test_stereotype_page_with_no_stereotype(self):
        ci = self.create(items.ClassItem, UML.Class)
        ci.subject.name = "Class"
        editor = StereotypePage(ci)
        page = editor.construct()
        assert page is None

    def test_stereotype_page_with_stereotype(self):
        # Create an stereotype applicable to Class types:
        metaclass = self.element_factory.create(UML.Class)
        metaclass.name = "Class"
        stereotype = self.element_factory.create(UML.Stereotype)
        stereotype.name = "NewStereotype"
        UML.model.create_extension(
                    self.element_factory, metaclass, stereotype
                )
        attr = self.element_factory.create(UML.Property)
        attr.name = "Property"
        # stereotype.ownedAttribute = attr

        ci = self.create(items.ClassItem, UML.Class)
        ci.subject.name = "Foo"
        editor = StereotypePage(ci)
        page = editor.construct()

        editor.refresh()
        assert len(editor.model) == 1
        assert page is not None


# vim:sw=4:et:ai
