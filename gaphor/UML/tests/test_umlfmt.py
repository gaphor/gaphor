"""Formatting of UML model elements into text tests."""

import pytest

from gaphor.core.eventmanager import EventManager
from gaphor.core.format import format, parse
from gaphor.core.modeling import ElementFactory
from gaphor.UML import recipes
from gaphor.UML import uml as UML
from gaphor.UML.umlfmt import format_association_end


@pytest.fixture
def factory():
    event_manager = EventManager()
    return ElementFactory(event_manager)


def add_tag_is_foo_metadata_field(e, factory):
    s = factory.create(UML.Stereotype)
    s.ownedAttribute = factory.create(UML.Property)
    parse(s.ownedAttribute[0], "tag: str")

    instance_spec = recipes.apply_stereotype(e, s)
    slot = recipes.add_slot(instance_spec, s.ownedAttribute[0])
    slot.value = "foo"
    return slot


@pytest.mark.parametrize(
    "text,formatted_text",
    [
        ("", ""),
        ("an attribute===foobar", "+ an attribute = ==foobar"),
        ("myattr", "+ myattr"),
        ("myattr:int", "+ myattr: int"),
        ("- myattr:int[3]", "- myattr: int[3]"),
        ("- myattr:int[0..1]", "- myattr: int[0..1]"),
        ("/myattr:int", "+ /myattr: int"),
        ("myattr:int=3", "+ myattr: int = 3"),
        ("myattr: int#some note", "+ myattr: int # some note"),
        ("# myattr:int=3 #some note", "# myattr: int = 3 # some note"),
        ("+ myattr: int | str", "+ myattr: int | str"),
    ],
)
def test_attribute(factory, text, formatted_text):
    """Test simple attribute formatting."""
    a = factory.create(UML.Property)
    parse(a, text)

    assert formatted_text == format(a, note=True)


def test_read_only_attribute(factory):
    a = factory.create(UML.Property)
    a.name = "myattr"
    a.isReadOnly = True

    assert "+ myattr { readOnly }" == format(a, tags=True)


def test_attribute_with_applied_stereotype(factory):
    a = factory.create(UML.Property)
    parse(a, "myattr: int")
    add_tag_is_foo_metadata_field(a, factory)

    assert '+ myattr: int { tag = "foo" }' == format(a, tags=True)


@pytest.mark.parametrize(
    "text,name_part, mult_part",
    [
        ("", "", ""),
        ("errorous (name)[3]", "+ errorous (name)[3]", ""),
        ("association end with spaces[3]", "+ association end with spaces", "3"),
        ("myattr", "+ myattr", ""),
        ("myattr[0..1]", "+ myattr", "0..1"),
        ("- myattr[0..1]", "- myattr", "0..1"),
    ],
)
def test_association_end(factory, text, name_part, mult_part):
    """Test simple attribute formatting."""
    a = factory.create(UML.Property)
    a.association = factory.create(UML.Association)
    parse(a, text)

    assert (name_part, mult_part) == format_association_end(a)


def test_attribute_with_type(factory):
    """Test simple attribute formatting."""
    a = factory.create(UML.Property)
    a.type = factory.create(UML.Class)
    a.name = "attr"
    a.type.name = "MyClass"

    assert "+ attr: MyClass" == format(a)


def test_association_end_with_applied_stereotype(factory):
    a = factory.create(UML.Property)
    a.association = factory.create(UML.Association)
    parse(a, "myattr[1]")
    add_tag_is_foo_metadata_field(a, factory)

    assert ("+ myattr", '1 { tag = "foo" }') == format_association_end(a)


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
        ("+ myoper(param: str): int#a note", "+ myoper(in param: str): int # a note"),
    ],
)
def test_operation(factory, text, formatted_text):
    """Test simple operation formatting."""
    o = factory.create(UML.Operation)
    parse(o, text)

    assert formatted_text == format(o, note=True)


@pytest.mark.parametrize(
    "text,formatted_text",
    [
        ("", ""),
        ("param", "in param"),
        ("in param: str", "in param: str"),
        ("param = val", "in param = val"),
    ],
)
def test_parameter(factory, text, formatted_text):
    """Test simple operation formatting."""
    p = factory.create(UML.Parameter)
    parse(p, text)

    assert formatted_text == format(p)


def test_slot(factory):
    a = factory.create(UML.Property)
    parse(a, "myattr: int")
    slot = add_tag_is_foo_metadata_field(a, factory)

    assert 'tag = "foo"' == format(slot)


def test_pin(factory):
    pin = factory.create(UML.InputPin)
    pin.name = "foo"

    pin.type = factory.create(UML.Class)
    pin.type.name = "MyClass"

    pin.lowerValue = "1"
    pin.upperValue = "*"

    assert format(pin) == "foo: MyClass[1..*]"
