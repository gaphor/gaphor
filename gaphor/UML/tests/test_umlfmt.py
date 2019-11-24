"""
Formatting of UML model elements into text tests.
"""

import pytest

import gaphor.UML.uml2 as UML
from gaphor.services.eventmanager import EventManager
from gaphor.UML import model
from gaphor.UML.elementfactory import ElementFactory
from gaphor.UML.umlfmt import format
from gaphor.UML.umllex import parse


@pytest.fixture
def factory():
    event_manager = EventManager()
    return ElementFactory(event_manager)


def add_tag_is_foo_metadata_field(e, factory):
    s = factory.create(UML.Stereotype)
    s.ownedAttribute = factory.create(UML.Property)
    parse(s.ownedAttribute[0], "tag: str")

    instance_spec = model.apply_stereotype(e, s)
    slot = model.add_slot(instance_spec, s.ownedAttribute[0])
    slot.value = "foo"
    return slot


@pytest.mark.parametrize(
    "text,formatted_text",
    [
        ("", ""),
        ("not an attribute===foobar", "+ not an attribute===foobar"),
        ("myattr", "+ myattr"),
        ("myattr:int", "+ myattr: int"),
        ("- myattr:int[3]", "- myattr: int[3]"),
        ("- myattr:int[0..1]", "- myattr: int[0..1]"),
        ("/myattr:int", "+ /myattr: int"),
        ("myattr:int=3", "+ myattr: int = 3"),
    ],
)
def test_attribute(factory, text, formatted_text):
    """Test simple attribute formatting
    """
    a = factory.create(UML.Property)
    parse(a, text)

    assert formatted_text == format(a)


def test_attribute_with_applied_stereotype(factory):
    a = factory.create(UML.Property)
    parse(a, "myattr: int")
    add_tag_is_foo_metadata_field(a, factory)

    assert '+ myattr: int { tag = "foo" }' == format(a, tags=True)


@pytest.mark.parametrize(
    "text,name_part, mult_part",
    [
        ("", "", ""),
        ("not an association end[3]", "+ not an association end[3]", ""),
        ("myattr", "+ myattr", ""),
        ("myattr[0..1]", "+ myattr", "0..1"),
        ("- myattr[0..1]", "- myattr", "0..1"),
    ],
)
def test_association_end(factory, text, name_part, mult_part):
    """Test simple attribute formatting
    """
    a = factory.create(UML.Property)
    a.association = factory.create(UML.Association)
    parse(a, text)

    assert (name_part, mult_part) == format(a)


def test_association_end_with_applied_stereotype(factory):
    a = factory.create(UML.Property)
    a.association = factory.create(UML.Association)
    parse(a, "myattr[1]")
    add_tag_is_foo_metadata_field(a, factory)

    assert ("+ myattr", '1 { tag = "foo" }') == format(a)


@pytest.mark.parametrize(
    "text,formatted_text",
    [
        ("", ""),
        ("not an operation", "+ not an operation()"),
        ("+ myoper(param: str): int", "+ myoper(in param: str): int"),
        ("+ myoper(param: str = 'aap')", "+ myoper(in param: str = 'aap')"),
        ("- myoper(out param: str): int[2]", "- myoper(out param: str): int[2]"),
        ("- myoper(out param: str): int[0..3]", "- myoper(out param: str): int[0..3]"),
        ("- myoper(p1: str[2], p2:int[*])", "- myoper(in p1: str[2], in p2: int[*])"),
        (
            "- myoper(p1: str[2], p2:int[1..*])",
            "- myoper(in p1: str[2], in p2: int[1..*])",
        ),
        ("+ (param: str): int", "+ (param: str): int"),
    ],
)
def test_operation(factory, text, formatted_text):
    """Test simple operation formatting
    """
    o = factory.create(UML.Operation)
    parse(o, text)

    assert formatted_text == format(o)


def test_slot(factory):
    a = factory.create(UML.Property)
    parse(a, "myattr: int")
    slot = add_tag_is_foo_metadata_field(a, factory)

    assert 'tag = "foo"' == format(slot)
