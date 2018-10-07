"""
Parsing of UML model elements from string tests.
"""

import unittest
from gaphor.application import Application
from gaphor.UML.elementfactory import ElementFactory
from gaphor.UML.umllex import parse
from gaphor.UML.umllex import attribute_pat, operation_pat, parameter_pat
from gaphor import UML

def dump_prop(prop):
    m = attribute_pat.match(prop)
    #print m.groupdict()

def dump_oper(oper):
    m = operation_pat.match(oper)
    if m:
        g = m.group
    else:
        # set name to oper
        return
    #print g('vis'), g('name'), g('type'), g('mult_l'), g('mult_u'), g('tags')
    if g('params'):
        params = g('params')
        while params:
            m = parameter_pat.match(params)
            g = m.group
            #print ' ', g('dir') or 'in', g('name'), g('type'), g('mult_l'), g('mult_u'), g('default'), g('tags')
            params = g('rest')

dump_prop('#/name')
dump_prop('+ / name : str[1..*] = "aap" { static }')
dump_prop('+ / name : str[*] = "aap" { static }')

dump_oper('myfunc(aap:str = "aap", out two): type')
dump_oper('   myfunc2 ( ): type')
dump_oper('myfunc(aap:str[1] = "aap" { tag1, tag2 }, out two {tag3}): type')


factory = ElementFactory()

class AttributeTestCase(unittest.TestCase):
    """
    Parsing an attribute tests.
    """
    def setUp(self):
        pass


    def tearDown(self):
        factory.flush()


    def test_parse_property_simple(self):
        """Test simple property parsing
        """
        a = factory.create(UML.Property)
        UML.parse(a, 'myattr')
        self.assertFalse(a.isDerived)
        self.assertEquals('myattr', a.name)
        self.assertTrue(a.typeValue is None, a.typeValue)
        self.assertTrue(a.lowerValue is None, a.lowerValue)
        self.assertTrue(a.upperValue is None, a.upperValue)
        self.assertTrue(a.defaultValue is None, a.defaultValue)


    def test_parse_property_complex(self):
        """Test complex property parsing
        """
        a = factory.create(UML.Property)

        UML.parse(a, '+ / name : str[0..*] = "aap" { static }')
        self.assertEquals('public', a.visibility)
        self.assertTrue(a.isDerived)
        self.assertEquals('name', a.name)
        self.assertEquals('str', a.typeValue)
        self.assertEquals('0', a.lowerValue)
        self.assertEquals('*', a.upperValue)
        self.assertEquals('"aap"', a.defaultValue)


    def test_parse_property_invalid(self):
        """Test parsing property with invalid syntax
        """
        a = factory.create(UML.Property)

        UML.parse(a, '+ name = str[*] = "aap" { static }')
        self.assertEquals('+ name = str[*] = "aap" { static }', a.name)
        self.assertFalse(a.isDerived)
        self.assertTrue(not a.typeValue)
        self.assertTrue(not a.lowerValue)
        self.assertTrue(not a.upperValue)
        self.assertTrue(not a.defaultValue)



class AssociationEndTestCase(unittest.TestCase):
    """
    Parsing association end tests.
    """
    def setUp(self):
        pass

    def tearDown(self):
        factory.flush()

    def test_parse_association_end(self):
        """Test parsing of association end
        """
        a = factory.create(UML.Association)
        p = factory.create(UML.Property)
        p.association = a

        UML.parse(p, 'end')
        self.assertEquals('end', p.name)
        self.assertTrue(not p.typeValue)
        self.assertTrue(not p.lowerValue)
        self.assertTrue(not p.upperValue)
        self.assertTrue(not p.defaultValue)


    def test_parse_multiplicity(self):
        """Test parsing of multiplicity
        """
        a = factory.create(UML.Association)
        p = factory.create(UML.Property)
        p.association = a
        UML.parse(p, '0..2 { tag }')
        self.assertTrue(p.name is None)
        self.assertTrue(not p.typeValue)
        self.assertEquals('0', p.lowerValue)
        self.assertEquals('2', p.upperValue)
        self.assertTrue(not p.defaultValue)


    def test_parse_multiplicity2(self):
        """Test parsing of multiplicity with multiline constraints
        """
        a = factory.create(UML.Association)
        p = factory.create(UML.Property)
        p.association = a
        UML.parse(p, '0..2 { tag1, \ntag2}')
        self.assertTrue(p.name is None)
        self.assertTrue(not p.typeValue)
        self.assertEquals('0', p.lowerValue)
        self.assertEquals('2', p.upperValue)
        self.assertTrue(not p.defaultValue)


    def test_parse_derived_end(self):
        """Test parsing derived association end
        """
        a = factory.create(UML.Association)
        p = factory.create(UML.Property)
        p.association = a
        UML.parse(p, '-/end[*] { mytag}')
        self.assertEquals('private', p.visibility)
        self.assertTrue(p.isDerived)
        self.assertEquals('end', p.name)
        self.assertTrue(not p.typeValue)
        self.assertTrue(not p.lowerValue)
        self.assertEquals('*', p.upperValue)
        self.assertTrue(not p.defaultValue)


class OperationTestCase(unittest.TestCase):
    """
    Operation parsing tests.
    """

    def setUp(self):
        factory.flush()

    def tearDown(self):
        factory.flush()

    def test_parse_operation(self):
        """Test parsing simple operation
        """
        o = factory.create(UML.Operation)
        UML.parse(o, 'myfunc()')
        self.assertEquals('myfunc', o.name)
        self.assertTrue(not o.returnResult[0].typeValue)
        self.assertFalse(o.formalParameter)


    def test_parse_operation_return(self):
        """Test parsing operation with return value
        """
        o = factory.create(UML.Operation)
        UML.parse(o, '+ myfunc(): int')
        self.assertEquals('myfunc', o.name)
        self.assertEquals('int', o.returnResult[0].typeValue)
        self.assertEquals('public', o.visibility)
        self.assertTrue(not o.formalParameter)


    def test_parse_operation_2_params(self):
        """Test parsing of operation with two parameters
        """
        o = factory.create(UML.Operation)
        UML.parse(o, '# myfunc2 (a: str, b: int = 3 {  static}): float')
        self.assertEquals('myfunc2', o.name)
        self.assertEquals('float', o.returnResult[0].typeValue)
        self.assertEquals('protected', o.visibility)
        self.assertEquals(2, len(o.formalParameter))
        self.assertEquals('a', o.formalParameter[0].name)
        self.assertEquals('str', o.formalParameter[0].typeValue)
        self.assertTrue(o.formalParameter[0].defaultValue is None)
        self.assertEquals('b', o.formalParameter[1].name)
        self.assertEquals('int', o.formalParameter[1].typeValue)
        self.assertEquals('3', o.formalParameter[1].defaultValue)


    def test_parse_operation_1_param(self):
        """Test parsing of operation with one parameter
        """
        o = factory.create(UML.Operation)
        UML.parse(o, '- myfunc2 (a: node): double')
        self.assertEquals('myfunc2', o.name)
        self.assertEquals('double', o.returnResult[0].typeValue)
        self.assertEquals('private', o.visibility)
        self.assertEquals(1, len(o.formalParameter))
        self.assertEquals('a', o.formalParameter[0].name)
        self.assertEquals('node', o.formalParameter[0].typeValue)
        self.assertTrue(o.formalParameter[0].defaultValue is None)


    def test_parse_operation_invalid_syntax(self):
        """Test operation parsing with invalid syntax
        """
        o = factory.create(UML.Operation)
        UML.parse(o, '- myfunc2: myType2')
        self.assertEquals('- myfunc2: myType2', o.name)


# vim:sw=4:et:ai
