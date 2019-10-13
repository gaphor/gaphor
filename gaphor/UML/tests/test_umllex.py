"""
Parsing of UML model elements from string tests.
"""

import pytest
from gaphor.services.eventmanager import EventManager
from gaphor.UML.elementfactory import ElementFactory
from gaphor.UML.umllex import attribute_pat, operation_pat, parameter_pat
from gaphor import UML


def dump_prop(prop):
    m = attribute_pat.match(prop)
    # print m.groupdict()


def dump_oper(oper):
    m = operation_pat.match(oper)
    if m:
        g = m.group
    else:
        # set name to oper
        return
    # print g('vis'), g('name'), g('type'), g('mult_l'), g('mult_u'), g('tags')
    if g("params"):
        params = g("params")
        while params:
            m = parameter_pat.match(params)
            g = m.group
            # print ' ', g('dir') or 'in', g('name'), g('type'), g('mult_l'), g('mult_u'), g('default'), g('tags')
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
    """Test simple property parsing
    """
    a = factory.create(UML.Property)
    UML.parse(a, "myattr")
    assert not a.isDerived
    assert "myattr" == a.name
    assert a.typeValue is None, a.typeValue
    assert a.lowerValue is None, a.lowerValue
    assert a.upperValue is None, a.upperValue
    assert a.defaultValue is None, a.defaultValue


def test_parse_property_complex(factory):
    """Test complex property parsing
    """
    a = factory.create(UML.Property)

    UML.parse(a, '+ / name : str[0..*] = "aap" { static }')
    assert "public" == a.visibility
    assert a.isDerived
    assert "name" == a.name
    assert "str" == a.typeValue
    assert "0" == a.lowerValue
    assert "*" == a.upperValue
    assert '"aap"' == a.defaultValue


def test_parse_property_invalid(factory):
    """Test parsing property with invalid syntax
    """
    a = factory.create(UML.Property)

    UML.parse(a, '+ name = str[*] = "aap" { static }')
    assert '+ name = str[*] = "aap" { static }' == a.name
    assert not a.isDerived
    assert not a.typeValue
    assert not a.lowerValue
    assert not a.upperValue
    assert not a.defaultValue


def test_parse_association_end(factory):
    """Test parsing of association end
    """
    a = factory.create(UML.Association)
    p = factory.create(UML.Property)
    p.association = a

    UML.parse(p, "end")
    assert "end" == p.name
    assert not p.typeValue
    assert not p.lowerValue
    assert not p.upperValue
    assert not p.defaultValue


def test_parse_association_end_multiplicity(factory):
    """Test parsing of multiplicity
    """
    a = factory.create(UML.Association)
    p = factory.create(UML.Property)
    p.association = a
    UML.parse(p, "0..2 { tag }")
    assert p.name is None
    assert not p.typeValue
    assert "0" == p.lowerValue
    assert "2" == p.upperValue
    assert not p.defaultValue


def test_parse_association_end_multiplicity2(factory):
    """Test parsing of multiplicity with multiline constraints
    """
    a = factory.create(UML.Association)
    p = factory.create(UML.Property)
    p.association = a
    UML.parse(p, "0..2 { tag1, \ntag2}")
    assert p.name is None
    assert not p.typeValue
    assert "0" == p.lowerValue
    assert "2" == p.upperValue
    assert not p.defaultValue


def test_parse_association_end_derived_end(factory):
    """Test parsing derived association end
    """
    a = factory.create(UML.Association)
    p = factory.create(UML.Property)
    p.association = a
    UML.parse(p, "-/end[*] { mytag}")
    assert "private" == p.visibility
    assert p.isDerived
    assert "end" == p.name
    assert not p.typeValue
    assert not p.lowerValue
    assert "*" == p.upperValue
    assert not p.defaultValue


def test_parse_operation(factory):
    """Test parsing simple operation
    """
    o = factory.create(UML.Operation)
    UML.parse(o, "myfunc()")
    assert "myfunc" == o.name
    assert not o.returnResult[0].typeValue
    assert not o.formalParameter


def test_parse_operation_return(factory):
    """Test parsing operation with return value
    """
    o = factory.create(UML.Operation)
    UML.parse(o, "+ myfunc(): int")
    assert "myfunc" == o.name
    assert "int" == o.returnResult[0].typeValue
    assert "public" == o.visibility
    assert not o.formalParameter


def test_parse_operation_2_params(factory):
    """Test parsing of operation with two parameters
    """
    o = factory.create(UML.Operation)
    UML.parse(o, "# myfunc2 (a: str, b: int = 3 {  static}): float")
    assert "myfunc2" == o.name
    assert "float" == o.returnResult[0].typeValue
    assert "protected" == o.visibility
    assert 2 == len(o.formalParameter)
    assert "a" == o.formalParameter[0].name
    assert "str" == o.formalParameter[0].typeValue
    assert o.formalParameter[0].defaultValue is None
    assert "b" == o.formalParameter[1].name
    assert "int" == o.formalParameter[1].typeValue
    assert "3" == o.formalParameter[1].defaultValue


def test_parse_operation_1_param(factory):
    """Test parsing of operation with one parameter
    """
    o = factory.create(UML.Operation)
    UML.parse(o, "- myfunc2 (a: node): double")
    assert "myfunc2" == o.name
    assert "double" == o.returnResult[0].typeValue
    assert "private" == o.visibility
    assert 1 == len(o.formalParameter)
    assert "a" == o.formalParameter[0].name
    assert "node" == o.formalParameter[0].typeValue
    assert o.formalParameter[0].defaultValue is None


def test_parse_operation_invalid_syntax(factory):
    """Test operation parsing with invalid syntax
    """
    o = factory.create(UML.Operation)
    UML.parse(o, "- myfunc2: myType2")
    assert "- myfunc2: myType2" == o.name
