"""Parsing of UML model elements from string tests."""

import pytest

from gaphor import UML
from gaphor.core.eventmanager import EventManager
from gaphor.core.format import parse
from gaphor.core.modeling import ElementFactory
from gaphor.UML.umllex import attribute_pat, operation_pat, parameters_pat


def dump_prop(prop):
    attribute_pat.match(prop)


def dump_oper(oper):
    if m := operation_pat.match(oper):
        g = m.group
    else:
        # set name to oper
        return
    if g("params"):
        params = g("params")
        while params:
            m = parameters_pat.match(params)
            g = m.group
            params = g("rest")


dump_prop("#/name")
dump_prop('+ / name : str[1..*] = "aap" { static }')
dump_prop('+ / name : str[*] = "aap" { static }')

dump_oper('myfunc(aap:str = "aap", out two): type')
dump_oper("   myfunc2 ( ): type")
dump_oper('myfunc(aap:str[1] = "aap" { tag1, tag2 }, out two {tag3}): type')


@pytest.fixture
def factory():
    event_manager = EventManager()
    return ElementFactory(event_manager)


def test_parse_property_simple(factory):
    """Test simple property parsing."""
    a = factory.create(UML.Property)
    parse(a, "myattr")
    assert not a.isDerived
    assert "myattr" == a.name
    assert a.typeValue is None, a.typeValue
    assert a.lowerValue is None, a.lowerValue
    assert a.upperValue is None, a.upperValue
    assert a.defaultValue is None, a.defaultValue


def test_parse_property_complex(factory):
    """Test complex property parsing."""
    a = factory.create(UML.Property)

    parse(a, '+ / name : str[0..*] = "aap" { static }# and a note')
    assert "public" == a.visibility
    assert a.isDerived
    assert "name" == a.name
    assert "str" == a.typeValue
    assert "0" == a.lowerValue
    assert "*" == a.upperValue
    assert '"aap"' == a.defaultValue
    assert "and a note" == a.note


def test_parse_property_with_space_in_name(factory):
    a = factory.create(UML.Property)

    parse(a, "+ name with space : str")

    assert "public" == a.visibility
    assert "name with space" == a.name
    assert "str" == a.typeValue


def test_parse_property_with_default_value_and_note(factory):
    a = factory.create(UML.Property)

    parse(a, "name=3 #note")

    assert "name" == a.name
    assert "3" == a.defaultValue
    assert "note" == a.note


def test_parse_property_with_square_brackets(factory):
    a = factory.create(UML.Property)
    parse(a, "attr[]")

    assert "attr" == a.name
    assert "*" == a.upperValue
    assert None is a.lowerValue


@pytest.mark.parametrize(
    "text,type_value",
    [
        ("attr: int | str", "int | str"),
        ("attr: int | str | bool | other", "int | str | bool | other"),
        ("attr: int|str|bool", "int|str|bool"),
        ("attr: my int|with space|some bool", "my int|with space|some bool"),
        ("attr: Generic type<Type>", "Generic type<Type>"),
        ("attr: Generic<Type> with extras", "Generic<Type> with extras"),
        ("attr: Generic<Type|Other>", "Generic<Type|Other>"),
    ],
)
def test_parse_property_with_union_type(factory, text, type_value):
    a = factory.create(UML.Property)
    parse(a, text)

    assert "attr" == a.name
    assert type_value == a.typeValue


def test_parse_property_invalid(factory):
    """Test parsing property with invalid syntax."""
    a = factory.create(UML.Property)

    parse(a, '+ name = str[*] = "aap" { static }')
    assert '+ name = str[*] = "aap" { static }' == a.name
    assert not a.isDerived
    assert not a.typeValue
    assert not a.lowerValue
    assert not a.upperValue
    assert not a.defaultValue


def test_parse_association_end(factory):
    """Test parsing of association end."""
    a = factory.create(UML.Association)
    p = factory.create(UML.Property)
    p.association = a

    parse(p, "end")
    assert "end" == p.name
    assert not p.typeValue
    assert not p.lowerValue
    assert not p.upperValue
    assert not p.defaultValue


def test_parse_association_end_multiplicity(factory):
    """Test parsing of multiplicity."""
    a = factory.create(UML.Association)
    p = factory.create(UML.Property)
    p.association = a
    parse(p, "0..2 { tag }")
    assert p.name is None
    assert not p.typeValue
    assert "0" == p.lowerValue
    assert "2" == p.upperValue
    assert not p.defaultValue


def test_parse_association_end_multiplicity2(factory):
    """Test parsing of multiplicity with multiline constraints."""
    a = factory.create(UML.Association)
    p = factory.create(UML.Property)
    p.association = a
    parse(p, "0..2 { tag1, \ntag2}")
    assert p.name is None
    assert not p.typeValue
    assert "0" == p.lowerValue
    assert "2" == p.upperValue
    assert not p.defaultValue


def test_parse_association_end_derived_end(factory):
    """Test parsing derived association end."""
    a = factory.create(UML.Association)
    p = factory.create(UML.Property)
    p.association = a
    parse(p, "-/end name[*] { mytag}")
    assert "private" == p.visibility
    assert p.isDerived
    assert "end name" == p.name
    assert not p.typeValue
    assert not p.lowerValue
    assert "*" == p.upperValue
    assert not p.defaultValue


def test_parse_association_end_with_type(factory):
    """Test parsing of association end, type is ignored."""
    a = factory.create(UML.Association)
    p = factory.create(UML.Property)
    p.association = a

    parse(p, "end: TypeVal")
    assert "end" == p.name
    assert not p.typeValue
    assert not p.lowerValue
    assert not p.upperValue
    assert not p.defaultValue


def test_parse_association_end_with_note(factory):
    a = factory.create(UML.Association)
    p = factory.create(UML.Property)
    p.association = a

    parse(p, "end # some note")
    assert "end" == p.name
    assert "some note" == p.note


def test_parse_association_end_with_square_brackets(factory):
    a = factory.create(UML.Association)
    p = factory.create(UML.Property)
    p.association = a

    parse(p, "end[]")
    assert "end" == p.name
    assert "*" == p.upperValue
    assert None is p.lowerValue


def test_parse_operation(factory):
    """Test parsing simple operation."""
    o = factory.create(UML.Operation)
    parse(o, "myfunc()")
    assert "myfunc" == o.name
    assert not o.ownedParameter


def test_parse_operation_return(factory):
    """Test parsing operation with return value."""
    o = factory.create(UML.Operation)
    parse(o, "+ myfunc(): int")
    assert "myfunc" == o.name
    assert "int" == o.ownedParameter[0].typeValue
    assert "public" == o.visibility


def test_parse_operation_2_params(factory):
    """Test parsing of operation with two parameters."""
    o = factory.create(UML.Operation)
    parse(o, "# myfunc2 (a: str, b: int = 3 {  static}): float")
    assert "myfunc2" == o.name
    assert "protected" == o.visibility
    assert len(o.ownedParameter) == 3
    assert "float" == o.ownedParameter[0].typeValue
    assert "a" == o.ownedParameter[1].name
    assert "str" == o.ownedParameter[1].typeValue
    assert o.ownedParameter[1].defaultValue is None
    assert "b" == o.ownedParameter[2].name
    assert "int" == o.ownedParameter[2].typeValue
    assert "3" == o.ownedParameter[2].defaultValue


def test_parse_operation_1_param(factory):
    """Test parsing of operation with one parameter."""
    o = factory.create(UML.Operation)
    parse(o, "- myfunc2 (a: node): double")
    assert "myfunc2" == o.name
    assert "private" == o.visibility
    assert len(o.ownedParameter) == 2
    assert "double" == o.ownedParameter[0].typeValue
    assert "a" == o.ownedParameter[1].name
    assert "node" == o.ownedParameter[1].typeValue
    assert o.ownedParameter[1].defaultValue is None


def test_parse_operation_with_spaces(factory):
    o = factory.create(UML.Operation)
    parse(o, "- name with space (param with space: some node ): return value")
    assert "name with space" == o.name
    assert "return value" == o.ownedParameter[0].typeValue
    assert "param with space" == o.ownedParameter[1].name
    assert "some node" == o.ownedParameter[1].typeValue


def test_parse_operation_with_union_types(factory):
    o = factory.create(UML.Operation)
    parse(o, "- oper(param with space: int | str ): bool | None")
    assert "oper" == o.name
    assert "bool | None" == o.ownedParameter[0].typeValue
    assert "int | str" == o.ownedParameter[1].typeValue
    assert "param with space" == o.ownedParameter[1].name


def test_parse_operation_invalid_syntax(factory):
    """Test operation parsing with invalid syntax."""
    o = factory.create(UML.Operation)
    parse(o, "- myfunc2: myType2")
    assert "- myfunc2: myType2" == o.name


def test_parse_operation_with_note(factory):
    """Test parsing simple operation."""
    o = factory.create(UML.Operation)
    parse(o, "myfunc() # and a note")
    assert "myfunc" == o.name
    assert "and a note" == o.note


def test_parse_operation_with_square_brackets(factory):
    o: UML.Operation = factory.create(UML.Operation)
    parse(o, "myfunc(args: string[])")
    p = o.ownedParameter[0]
    assert "args" == p.name
    assert "string" == p.typeValue
    assert "*" == p.upperValue
    assert None is p.lowerValue


def test_parse_operation_return_with_square_brackets(factory):
    o: UML.Operation = factory.create(UML.Operation)
    parse(o, "myfunc(): string[]")
    p = o.ownedParameter[0]
    assert "return" == p.direction
    assert "string" == p.typeValue
    assert "*" == p.upperValue
    assert None is p.lowerValue


@pytest.mark.parametrize(
    "operation,type_value",
    [
        ["+ test(param: Generic<Type>)", "Generic<Type>"],
        ["+ test(param: Generic with space <Type>)", "Generic with space <Type>"],
        [
            "+ test(param: Generic with space <Type> | Other<Type|Other>)",
            "Generic with space <Type> | Other<Type|Other>",
        ],
        [
            "+ test(param: Generic <Type> | Other<Type> | Third<Type>)",
            "Generic <Type> | Other<Type> | Third<Type>",
        ],
    ],
)
def test_parse_operation_with_template_attribute(operation, type_value, factory):
    o: UML.Operation = factory.create(UML.Operation)
    parse(o, operation)
    p = o.ownedParameter[0]
    assert "param" == p.name
    assert type_value == p.typeValue
