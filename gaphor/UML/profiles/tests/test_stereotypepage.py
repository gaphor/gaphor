"""Test Stereotype Property Page."""

from gi.repository import Gtk

from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.profiles.stereotypepropertypages import StereotypePage


def test_stereotype_page_with_no_stereotype(element_factory):
    subject = element_factory.create(UML.Class)

    editor = StereotypePage(subject)
    page = editor.construct()

    assert page is None


def test_stereotype_page_with_stereotype(element_factory):
    subject = element_factory.create(UML.Class)

    # Create a stereotype applicable to Class types:
    metaclass = element_factory.create(UML.Class)
    metaclass.name = "Class"
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "NewStereotype"
    UML.recipes.create_extension(metaclass, stereotype)
    attr = element_factory.create(UML.Property)
    attr.name = "Property"

    editor = StereotypePage(subject)
    page = editor.construct()

    stereotype_view = find(page, "stereotype-list")

    assert isinstance(stereotype_view, Gtk.ColumnView)
    assert len(stereotype_view.get_model()) == 1
    assert page is not None
