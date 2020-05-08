"""Test Stereotype Property Page."""

import pytest
from gi.repository import Gtk

from gaphor import UML
from gaphor.UML.classes.klass import ClassItem
from gaphor.UML.profiles.stereotypepropertypages import StereotypePage


@pytest.fixture
def class_(diagram, element_factory):
    class_ = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    class_.name = "Class"
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
    UML.model.create_extension(metaclass, stereotype)
    attr = element_factory.create(UML.Property)
    attr.name = "Property"

    editor = StereotypePage(class_)
    page = editor.construct()

    box = page.get_children()[0]
    frame = box.get_children()[1]
    stereotype_view = frame.get_children()[0]

    assert isinstance(stereotype_view, Gtk.TreeView)
    assert len(stereotype_view.get_model()) == 1
    assert page is not None
