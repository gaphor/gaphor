"""
Formatting of UML elements like attributes, operations, stereotypes, etc.
"""

import re
from cStringIO import StringIO
from simplegeneric import generic

from gaphor.UML import uml2 as UML


@generic
def format(el, pattern=None):
    """
    Format an UML element.
    """
    raise NotImplementedError('Format routine for type %s not implemented yet' \
            % type(el))


@format.when_type(UML.Property)
def format_attribute(el, pattern=None, *args, **kwargs):
    """
    Format property or an association end.
    """
    if el.association:
        return format_association_end(el)
    else:
        return format_attribute(el, *args, **kwargs)


def compile(regex):
    return re.compile(regex, re.MULTILINE | re.S)


# Do not render if the name still contains a visibility element
no_render_pat = compile(r'^\s*[+#-]')
vis_map = {
    'public': '+',
    'protected': '#',
    'package': '~',
    'private': '-'
}


def format_attribute(el, visibility=False, is_derived=False, type=False,
                           multiplicity=False, default=False, tags=False):
    """
    Create a OCL representation of the attribute,
    Returns the attribute as a string.
    If one or more of the parameters (visibility, is_derived, type,
    multiplicity, default and/or tags) is set, only that field is rendered.
    Note that the name of the attribute is always rendered, so a parseable
    string is returned.

    Note that, when some of those parameters are set, parsing the string
    will not give you the same result.
    """
    name = el.name
    if not name:
        name = ''

    if no_render_pat.match(name):
        name = ''

    # Render all fields if they all are set to False
    if not (visibility or is_derived or type or multiplicity or default):
       visibility = is_derived = type = multiplicity = default = True

    s = StringIO()

    if visibility:
        s.write(vis_map[el.visibility])
        s.write(' ')

    if is_derived:
        if el.isDerived: s.write('/')

    s.write(name)
    
    if type and el.typeValue and el.typeValue.value:
        s.write(': %s' % el.typeValue.value)

    if multiplicity and el.upperValue and el.upperValue.value:  
        if el.lowerValue and el.lowerValue.value:
            s.write('[%s..%s]' % (el.lowerValue.value, el.upperValue.value))
        else:
            s.write('[%s]' % el.upperValue.value)

    if default and el.defaultValue and el.defaultValue.value:
        s.write(' = %s' % el.defaultValue.value)

    if tags:
        slots = []
        for slot in el.appliedStereotype[:].slot:
            if slot.value:
                slots.append('%s=%s' % (slot.definingFeature.name, slot.value.value))
        if slots:
            s.write(' { %s }' % ', '.join(slots))
    s.reset()
    return s.read()


def format_association_end(el):
    """
    Format association end.
    """
    name = ''
    n = StringIO()
    if el.name:
        n.write(vis_map[el.visibility])
        n.write(' ')
        if el.isDerived:
            n.write('/')
        if el.name:
            n.write(el.name)
        n.reset()
        name = n.read()

    m = StringIO()
    if el.upperValue and el.upperValue.value:  
        if el.lowerValue and el.lowerValue.value:
            m.write('%s..%s' % (el.lowerValue.value, el.upperValue.value))
        else:
            m.write('%s' % el.upperValue.value)

    slots = []
    for slot in el.appliedStereotype[:].slot:
        if slot.value:
            slots.append('%s=%s' % (slot.definingFeature.name, slot.value.value))
    if slots:
        m.write(' { %s }' % ',\n'.join(slots))
    m.reset()
    mult = m.read()

    return name, mult


@format.when_type(UML.Operation)
def format_operation(el, pattern=None, visibility=False, type=False, multiplicity=False,
                           default=False, tags=False, direction=False):
    """
    Create a OCL representation of the operation,
    Returns the operation as a string.
    """
    name = el.name
    if not name:
        return ''
    if no_render_pat.match(name):
        return name

    # Render all fields if they all are set to False
    if not (visibility or type or multiplicity or default or tags or direction):
       visibility = type = multiplicity = default = tags = direction = True

    s = StringIO()
    if visibility:
        s.write(vis_map[el.visibility])
        s.write(' ')

    s.write(name)
    s.write('(')

    for p in el.formalParameter:
        if direction:
            s.write(p.direction)
            s.write(' ')
        s.write(p.name)
        if type and p.typeValue and p.typeValue.value:
            s.write(': %s' % p.typeValue.value)
        if multiplicity and p.upperValue and p.upperValue.value:  
            if p.lowerValue and p.lowerValue.value:
                s.write('[%s..%s]' % (p.lowerValue.value, p.upperValue.value))
            else:
                s.write('[%s]' % p.upperValue.value)
        if default and p.defaultValue and p.defaultValue.value:
            s.write(' = %s' % p.defaultValue.value)
        #if p.taggedValue:
        #     tvs = ', '.join(filter(None, map(getattr, p.taggedValue,
        #                                      ['value'] * len(p.taggedValue))))
        #     s.write(' { %s }' % tvs)
        if p is not el.formalParameter[-1]:
            s.write(', ')

    s.write(')')

    rr = el.returnResult and el.returnResult[0]
    if rr:
        if type and rr.typeValue and rr.typeValue.value:
            s.write(': %s' % rr.typeValue.value)
        if multiplicity and rr.upperValue and rr.upperValue.value:  
            if rr.lowerValue and rr.lowerValue.value:
                s.write('[%s..%s]' % (rr.lowerValue.value, rr.upperValue.value))
            else:
                s.write('[%s]' % rr.upperValue.value)
        #if rr.taggedValue:
        #    tvs = ', '.join(filter(None, map(getattr, rr.taggedValue,
        #                                     ['value'] * len(rr.taggedValue))))
        #    if tvs:
        #        s.write(' { %s }' % tvs)
    s.reset()
    return s.read()


@format.when_type(UML.Slot)
def format_slot(el, pattern=None):
    return '%s = "%s"' % (el.definingFeature.name, el.value.value)


@format.when_type(UML.NamedElement)
def format_namedelement(el, pattern='%s'):
    """
    Format named element.
    """
    return pattern % el.name


