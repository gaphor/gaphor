from gaphor.UML import *
from gaphor.UML.umllex import *
from gaphor.UML.umllex import property_pat, operation_pat, parameter_pat

# Add some extra associations that have to be added to the model:
#Parameter.typeValue = association('typeValue', ValueSpecification, upper=1, composite=True)
#Parameter.taggedValue = association('taggedValue', ValueSpecification, upper=1, composite=True)
#Property.typeValue = association('typeValue', ValueSpecification, upper=1, composite=True)
#Property.taggedValue = association('taggedValue', ValueSpecification, upper=1, composite=True)

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

element_factory = GaphorResource(ElementFactory)
log.set_log_level(log.INFO)

print 'testing parse_operation()...',
o = element_factory.create(Operation)
assert len(element_factory.values()) == 1

# Very simple procedure:

parse_operation(o, 'myfunc()')
assert o.visibility == 'public'
assert o.name == 'myfunc', o.name
assert o.returnResult[0].typeValue.value is None, o.returnResult[0].typeValue.value
assert not o.formalParameter, o.formalParameter
# 1 operation, 1 parameter, 4 literal strings.
assert len(element_factory.values()) == 6, len(element_factory.values())

# Procedure with return value:

parse_operation(o, '# myfunc(): myType')
assert o.name == 'myfunc', o.name
assert o.returnResult[0].typeValue.value == 'myType', o.returnResult[0].typeValue.value
assert o.visibility == 'protected'
assert not o.formalParameter, o.formalParameter
assert len(element_factory.values()) == 6, len(element_factory.values())

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

# Change the operation to own one parameter:

parse_operation(o, '# myfunc2 (a: node): myType2')
assert o.name == 'myfunc2', o.name
assert o.returnResult[0].typeValue.value == 'myType2', o.returnResult[0].typeValue.value
assert o.visibility == 'protected'
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

print 'done'

