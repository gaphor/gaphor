"""Test Stereotype Property Page."""

import pytest
from gi.repository import Gtk

from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.classes.klass import ClassItem
from gaphor.UML.profiles.stereotypepropertypages import StereotypePage


@pytest.fixture
def class_(diagram, element_factory):
    class_ = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    class_.subject.name = "Class"
    yield class_
    del class_


def test_stereotype_page_with_no_stereotype(diagram, class_):
    """Test the Stereotype Property Page not created for a Class."""

    editor = StereotypePage(class_)
    page = editor.construct()

    assert page is None


def test_stereotype_page_with_stereotype(element_factory, diagram, class_):
    """Test creation of a Stereotype Property Page."""

    # Create a stereotype applicable to Class types:
    metaclass = element_factory.create(UML.Class)
    metaclass.name = "Class"
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "NewStereotype"
    UML.recipes.create_extension(metaclass, stereotype)
    attr = element_factory.create(UML.Property)
    attr.name = "Property"

    editor = StereotypePage(class_)
    page = editor.construct()

    stereotype_view = find(page, "stereotype-list")

    assert isinstance(stereotype_view, Gtk.TreeView)
    assert len(stereotype_view.get_model()) == 1
    assert page is not None
