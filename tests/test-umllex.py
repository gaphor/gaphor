
import gaphor
from gaphor.UML import *
from gaphor.UML.umllex import *
from gaphor.UML.umllex import property_pat, operation_pat, parameter_pat

def dump_prop(prop):
    m = property_pat.match(prop)
    g = m.group
    print g('vis'), g('derived'), g('name'), g('type'), g('mult_l'), g('mult_u'), g('default'), g('tags')

def dump_oper(oper):
    m = operation_pat.match(oper)
    if m:
        g = m.group
    else:
        # set name to oper
        return
    print g('vis'), g('name'), g('type'), g('mult_l'), g('mult_u'), g('tags')
    if g('params'):
        params = g('params')
        while params:
            m = parameter_pat.match(params)
            g = m.group
            print ' ', g('dir') or 'in', g('name'), g('type'), g('mult_l'), g('mult_u'), g('default'), g('tags')
            params = g('rest')

dump_prop('#/name')
dump_prop('+ / name : str[1..*] = "aap" { static }')
dump_prop('+ / name : str[*] = "aap" { static }')

dump_oper('myfunc(aap:str = "aap", out two): type')
dump_oper('   myfunc2 ( ): type')
dump_oper('myfunc(aap:str[1] = "aap" { tag1, tag2 }, out two {tag3}): type')

element_factory = gaphor.resource(ElementFactory)
log.set_log_level(log.INFO)

print 'testing parse_attribute()...'
a = element_factory.create(Property)
assert len(element_factory.values()) == 1

# Very simple:

parse_attribute(a, 'myattr')
assert a.visibility == 'protected'
assert a.isDerived == False, a.isDerived
assert a.name == 'myattr', a.name
assert a.typeValue.value is None, a.typeValue.value 
assert a.lowerValue.value is None, a.lowerValue.value 
assert a.upperValue.value is None, a.upperValue.value 
assert a.defaultValue.value is None, a.defaultValue.value 
assert a.taggedValue.value is None, a.taggedValue.value 
s = render_attribute(a)
parse_attribute(a, s)
assert s == render_attribute(a)

# All features:
a.unlink()
a = element_factory.create(Property)

parse_attribute(a,'+ / name : str[0..*] = "aap" { static }')
assert a.visibility == 'public'
assert a.isDerived == True, a.isDerived
assert a.name == 'name', a.name
assert a.typeValue.value == 'str', a.typeValue.value 
assert a.lowerValue.value == '0', a.lowerValue.value 
assert a.upperValue.value == '*', a.upperValue.value 
assert a.defaultValue.value == '"aap"', a.defaultValue.value 
assert a.taggedValue.value == 'static', a.taggedValue.value 
s = render_attribute(a)
parse_attribute(a, s)
assert s == render_attribute(a)
print render_attribute(a)

# Invalid syntax:
a.unlink()
a = element_factory.create(Property)

parse_attribute(a, '+ name = str[*] = "aap" { static }')
assert a.visibility == 'protected'
assert a.isDerived == False, a.isDerived
assert a.name == '+ name = str[*] = "aap" { static }', a.name
assert not a.typeValue or a.typeValue.value is None, a.typeValue.value 
assert not a.lowerValue or a.lowerValue.value is None, a.lowerValue.value 
assert not a.upperValue or a.upperValue.value is None, a.upperValue.value 
assert not a.defaultValue or a.defaultValue.value is None, a.defaultValue.value 
assert not a.taggedValue or a.taggedValue.value is None, a.taggedValue.value 
s = render_attribute(a)
parse_attribute(a, s)
assert s == render_attribute(a)
print render_attribute(a)

# Cleanup

a.unlink()
assert len(element_factory.values()) == 0

print 'testing parse_operation()...'
o = element_factory.create(Operation)
assert len(element_factory.values()) == 1

# Very simple procedure:

parse_operation(o, 'myfunc()')
assert o.visibility == 'protected'
assert o.name == 'myfunc', o.name
assert o.returnResult[0].typeValue.value is None, o.returnResult[0].typeValue.value
assert not o.formalParameter, o.formalParameter
# 1 operation, 1 parameter, 4 literal strings.
assert len(element_factory.values()) == 6, len(element_factory.values())
s = render_operation(o)
print render_operation(o)
parse_operation(o, s)
assert s == render_operation(o)

# Procedure with return value:

parse_operation(o, '+ myfunc(): myType')
assert o.name == 'myfunc', o.name
assert o.returnResult[0].typeValue.value == 'myType', o.returnResult[0].typeValue.value
assert o.visibility == 'public'
assert not o.formalParameter, o.formalParameter
assert len(element_factory.values()) == 6, len(element_factory.values())
s = render_operation(o)
parse_operation(o, s)
assert s == render_operation(o)
print render_operation(o)

# Change the operation to support two parameters:

parse_operation(o, '# myfunc2 (a: str, b: int = 3 {  static}): myType2')
assert o.name == 'myfunc2', o.name
assert o.returnResult[0].typeValue.value == 'myType2', o.returnResult[0].typeValue.value
assert o.visibility == 'protected'
assert len(o.formalParameter) == 2, o.formalParameter
assert o.formalParameter[0].name == 'a', o.formalParameter[0].typeValue
assert o.formalParameter[0].typeValue.value == 'str', o.formalParameter[0].typeValue.value
assert o.formalParameter[0].defaultValue.value is None, o.formalParameter[0].defaultValue.value
assert o.formalParameter[0].taggedValue.value is None, o.formalParameter[0].taggedValue.value
assert o.formalParameter[1].name == 'b', o.formalParameter[1].name
assert o.formalParameter[1].typeValue.value == 'int', o.formalParameter[1].typeValue.value
assert o.formalParameter[1].defaultValue.value == '3', o.formalParameter[1].defaultValue.value
assert o.formalParameter[1].taggedValue.value == 'static', o.formalParameter[1].taggedValue.value
# 1 operation, 3 parameters, 4 + 5*2 literal strings
assert len(element_factory.select(lambda e: isinstance(e, LiteralString))) == 14, len(element_factory.select(lambda e: isinstance(e, LiteralString)))
assert len(element_factory.values()) == 18, len(element_factory.values())
s = render_operation(o)
parse_operation(o, s)
assert s == render_operation(o)

print render_operation(o)

# Change the operation to own one parameter:

parse_operation(o, '- myfunc2 (a: node): myType2')
assert o.name == 'myfunc2', o.name
assert o.returnResult[0].typeValue.value == 'myType2', o.returnResult[0].typeValue.value
assert o.visibility == 'private'
assert len(o.formalParameter) == 1, o.formalParameter
assert o.formalParameter[0].name == 'a', o.formalParameter[0].typeValue
assert o.formalParameter[0].typeValue.value == 'node', o.formalParameter[0].typeValue.value
assert o.formalParameter[0].defaultValue.value is None, o.formalParameter[0].defaultValue.value
assert o.formalParameter[0].taggedValue.value is None, o.formalParameter[0].taggedValue.value
# 1 operation, 2 parameters, 4 + 5 literal strings
assert len(element_factory.select(lambda e: isinstance(e, Operation))) == 1, len(element_factory.values())
assert len(element_factory.select(lambda e: isinstance(e, Parameter))) == 2, len(element_factory.values())
assert len(element_factory.select(lambda e: isinstance(e, LiteralString))) == 9, len(element_factory.select(lambda e: isinstance(e, LiteralString)))
assert len(element_factory.values()) == 12, len(element_factory.values())
print render_operation(o)
s = render_operation(o)
parse_operation(o, s)
assert s == render_operation(o)

print 'done'

