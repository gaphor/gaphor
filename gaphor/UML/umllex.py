#!/usr/bin/env python
# vim:sw=4:et
"""Lexical analizer for attributes and operations.

In this module some parse functions are added for attributes and operations.
The regular expressions are constructed based on a series of
"sub-patterns". This makes it easy to identify the autonomy of an
attribute/operation.
"""

__all__ = [ 'parse_property', 'parse_operation', 'render_property', 'render_operation' ]

import re
from cStringIO import StringIO
import gaphor

# Visibility (optional) ::= '+' | '-' | '#'
vis_subpat = r'\s*(?P<vis>[-+#])?'

# Derived value (optional) ::= [/]
derived_subpat = r'\s*(?P<derived>/)?'

# name (required) ::= name
name_subpat = r'\s*(?P<name>[a-zA-Z_]\w*)'

# Multiplicity (added to type_subpat) ::= '[' [mult_l ..] mult_u ']'
mult_subpat = r'\s*(\[\s*((?P<mult_l>[0-9]+)\s*\.\.)?\s*(?P<mult_u>([0-9]+|\*))\s*\])?'
multa_subpat = r'\s*(\[?((?P<mult_l>[0-9]+)\s*\.\.)?\s*(?P<mult_u>([0-9]+|\*))\]?)?'

# Type and multiplicity (optional) ::= ':' type [mult]
type_subpat = r'\s*(:\s*(?P<type>\w+)\s*' + mult_subpat + r')?'

# default value (optional) ::= '=' default
default_subpat = r'\s*(=\s*(?P<default>\S+))?'

# tagged values (optional) ::= '{' tags '}'
tags_subpat = r'\s*(\{\s*(?P<tags>.*?)\s*\})?'

# Parameters (required) ::= '(' [params] ')'
params_subpat = r'\s*\(\s*(?P<params>[^)]+)?\)'

# Possible other parameters (optional) ::= ',' rest
rest_subpat = r'\s*(,\s*(?P<rest>.*))?'

# Direction of a parameter (optional, default in) ::= 'in' | 'out' | 'inout'
dir_subpat = r'\s*((?P<dir>in|out|inout)\s)?'

# Some trailing garbage => no valid syntax...
garbage_subpat = r'\s*(?P<garbage>.*)'

def compile(regex):
    return re.compile(regex, re.MULTILINE | re.S)

# Attribute:
#   [+-#] [/] name [: type[\[mult\]]] [= default] [{ tagged values }]
attribute_pat = compile(r'^' + vis_subpat + derived_subpat + name_subpat + type_subpat + default_subpat + tags_subpat + garbage_subpat)

# Association end name:
#   [[+-#] [/] name [\[mult\]]] [{ tagged values }]
association_end_name_pat = compile(r'^' + '(' + vis_subpat + derived_subpat + name_subpat + mult_subpat + ')?' + tags_subpat + garbage_subpat)

# Association end multiplicity:
#   [mult] [{ tagged values }]
association_end_mult_pat = compile(r'^' + multa_subpat + tags_subpat + garbage_subpat)

# Operation:
#   [+|-|#] name ([parameters]) [: type[\[mult\]]] [{ tagged values }]
operation_pat = compile(r'^' + vis_subpat + name_subpat + params_subpat + type_subpat + tags_subpat + garbage_subpat)

# One parameter supplied with an operation:
#   [in|out|inout] name [: type[\[mult\]] [{ tagged values }]
parameter_pat = compile(r'^' + dir_subpat + name_subpat + type_subpat + default_subpat + tags_subpat + rest_subpat)

# Lifeline:
#  [name] [: type]
lifeline_pat = compile('^' + name_subpat + type_subpat + garbage_subpat)

def _set_visibility(self, vis):
    if vis == '+':
        self.visibility = 'public'
    elif vis == '#':
        self.visibility = 'protected'
    elif vis == '~':
        self.visibility = 'package'
    elif vis == '-':
        self.visibility = 'private'
    else:
        try:
            del self.visibility
        except AttributeError:
            pass

def parse_attribute(self, s):
    """
    Parse string s in the property. Tagged values, multiplicity and stuff
    like that is altered to reflect the data in the property string.
    """
    m = attribute_pat.match(s)
    g = m.group
    if not m or g('garbage'):
        self.name = s
        del self.visibility
        del self.isDerived
        if self.typeValue:
            self.typeValue.value = None
        if self.lowerValue:
            self.lowerValue.value = None
        if self.upperValue:
            self.upperValue.value = None
        if self.defaultValue:
            self.defaultValue.value = None
        #if self.taggedValue:
        #    self.taggedValue.value = None
        while self.taggedValue:
            self.taggedValue[0].unlink()
    else:
        from uml2 import LiteralSpecification
        create = self._factory.create
        _set_visibility(self, g('vis'))
        self.isDerived = g('derived') and True or False
        self.name = g('name')
        if not self.typeValue:
            self.typeValue = create(LiteralSpecification)
        self.typeValue.value = g('type')
        if not self.lowerValue:
            self.lowerValue = create(LiteralSpecification)
        self.lowerValue.value = g('mult_l')
        if not self.upperValue:
            self.upperValue = create(LiteralSpecification)
        self.upperValue.value = g('mult_u')
        if not self.defaultValue:
            self.defaultValue = create(LiteralSpecification)
        self.defaultValue.value = g('default')
        while self.taggedValue:
            self.taggedValue[0].unlink()
        tags = g('tags')
        if tags:
            for t in map(str.strip, tags.split(',')):
                tv = create(LiteralSpecification)
                tv.value = t
                self.taggedValue = tv


def parse_association_end(self, s):
    """
    Parse the text at one end of an association. The association end holds
    two strings. It is automattically figured out which string is fed to the
    parser.
    """
    from uml2 import LiteralSpecification
    create = self._factory.create

    # if no name, then clear as there could be some garbage
    # due to previous parsing (i.e. '[1'
    m = association_end_name_pat.match(s)
    if m and not m.group('name'):
        self.name = ''

    m = association_end_mult_pat.match(s)
    if m and m.group('mult_u') or m.group('tags'):
        g = m.group
        if not self.lowerValue:
            self.lowerValue = create(LiteralSpecification)
        self.lowerValue.value = g('mult_l')
        if not self.upperValue:
            self.upperValue = create(LiteralSpecification)
        self.upperValue.value = g('mult_u')
        while self.taggedValue:
            self.taggedValue[0].unlink()
        tags = g('tags')
        if tags:
            for t in map(str.strip, tags.split(',')):
                tv = create(LiteralSpecification)
                tv.value = t
                self.taggedValue = tv
    else:
        m = association_end_name_pat.match(s)
        g = m.group
        if g('garbage'):
            self.name = s
            del self.visibility
            del self.isDerived
        else:
            _set_visibility(self, g('vis'))
            self.isDerived = g('derived') and True or False
            self.name = g('name')
            # Optionally, the multiplicity and tagged values may be defined:
            if g('mult_l'):
                if not self.lowerValue:
                    self.lowerValue = create(LiteralSpecification)
                self.lowerValue.value = g('mult_l')

            if g('mult_u'):
                if not g('mult_l') and self.lowerValue:
                    self.lowerValue.value = None
                if not self.upperValue:
                    self.upperValue = create(LiteralSpecification)
                self.upperValue.value = g('mult_u')

            tags = g('tags')
            if tags:
                while self.taggedValue:
                    self.taggedValue[0].unlink()
                for t in map(str.strip, tags.split(',')):
                    tv = create(LiteralSpecification)
                    tv.value = t
                    self.taggedValue = tv

def parse_property(self, s):
    if self.association:
        parse_association_end(self, s)
    else:
        parse_attribute(self, s)

def parse_operation(self, s):
    """
    Parse string s in the operation. Tagged values, parameters and
    visibility is altered to reflect the data in the operation string.
    """
    from uml2 import Parameter, LiteralSpecification
    m = operation_pat.match(s)
    if not m or m.group('garbage'):
        self.name = s
        del self.visibility
        map(Parameter.unlink, list(self.returnResult))
        map(Parameter.unlink, list(self.formalParameter))
    else:
        g = m.group
        create = self._factory.create
        _set_visibility(self, g('vis'))
        self.name = g('name')
        if not self.returnResult:
            self.returnResult = create(Parameter)
        p = self.returnResult[0]
        p.direction = 'return'
        if not p.typeValue:
            p.typeValue = create(LiteralSpecification)
        p.typeValue.value = g('type')
        if not p.lowerValue:
            p.lowerValue = create(LiteralSpecification)
        p.lowerValue.value = g('mult_l')
        if not p.upperValue:
            p.upperValue = create(LiteralSpecification)
        p.upperValue.value = g('mult_u')
        # FIXME: Maybe add to Operation.ownedRule?
        while self.taggedValue:
            self.taggedValue[0].unlink()
        tags = g('tags')
        if tags:
            for t in map(str.strip, tags.split(',')):
                tv = create(LiteralSpecification)
                tv.value = t
                p.taggedValue = tv
        
        pindex = 0
        params = g('params')
        while params:
            m = parameter_pat.match(params)
            if not m:
                break
            g = m.group
            try:
                p = self.formalParameter[pindex]
            except IndexError:
                p = create(Parameter)
            p.direction = g('dir') or 'in'
            p.name = g('name')
            if not p.typeValue:
                p.typeValue = create(LiteralSpecification)
            p.typeValue.value = g('type')
            if not p.lowerValue:
                p.lowerValue = create(LiteralSpecification)
            p.lowerValue.value = g('mult_l')
            if not p.upperValue:
                p.upperValue = create(LiteralSpecification)
            p.upperValue.value = g('mult_u')
            if not p.defaultValue:
                p.defaultValue = create(LiteralSpecification)
            p.defaultValue.value = g('default')
            while p.taggedValue:
                p.taggedValue[0].unlink()
            tags = g('tags')
            if tags:
                for t in map(str.strip, tags.split(',')):
                    tv = create(LiteralSpecification)
                    tv.value = t
                    p.taggedValue = tv
            self.formalParameter = p

            # Do the next parameter:
            params = g('rest')
            pindex += 1

        # Remove remaining parameters:
        for fp in self.formalParameter[pindex:]:
            fp.unlink()

def parse_lifeline(self, s):
    """
    Parse string s in a lifeline. If a class is defined and can be found
    in the datamodel, then a class is connected to the lifelines 'represents'
    property.
    """
    m = lifeline_pat.match(s)
    g = m.group
    if not m or g('garbage'):
        self.name = s
        if hasattr(self, 'represents'):
            del self.represents
    else:
        from uml2 import LiteralSpecification
        self.name = g('name') + ": "
        t = g('type')
        if t:
            self.name += ': ' + t
        # In the near future the data model should be extended with 
        # Lifeline.represents: ConnectableElement

# Do not render if the name still contains a visibility element
no_render_pat = compile(r'^\s*[+#-]')
vis_map = {
    'public': '+',
    'protected': '#',
    'package': '~',
    'private': '-'
}


def render_attribute(self, visibility=False, is_derived=False, type=False,
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
    name = self.name
    if not name:
        return ''

    if not name or no_render_pat.match(name):
        return name

    # Render all fields if they all are set to False
    if not (visibility or is_derived or type or multiplicity or default or tags):
       visibility = is_derived = type = multiplicity = default = tags = True

    s = StringIO()

    if visibility:
        s.write(vis_map[self.visibility])
        s.write(' ')

    if is_derived:
        if self.isDerived: s.write('/')

    s.write(name)
    
    if type and self.typeValue and self.typeValue.value:
        s.write(': %s' % self.typeValue.value)

    if multiplicity and self.upperValue and self.upperValue.value:  
        if self.lowerValue and self.lowerValue.value:
            s.write('[%s..%s]' % (self.lowerValue.value, self.upperValue.value))
        else:
            s.write('[%s]' % self.upperValue.value)

    if default and self.defaultValue and self.defaultValue.value:
        s.write(' = %s' % self.defaultValue.value)

    if self.taggedValue:
        tvs = ', '.join(filter(None, map(getattr, self.taggedValue,
                                          ['value'] * len(self.taggedValue))))
        if tvs:
            s.write(' { %s }' % tvs)
    s.reset()
    return s.read()


def render_association_end(self):
    """
    """
    name = ''
    n = StringIO()
    if self.name:
        n.write(vis_map[self.visibility])
        n.write(' ')
        if self.isDerived:
            n.write('/')
        if self.name:
            n.write(self.name)
        n.reset()
        name = n.read()

    m = StringIO()
    if self.upperValue and self.upperValue.value:  
        if self.lowerValue and self.lowerValue.value:
            m.write('%s..%s' % (self.lowerValue.value, self.upperValue.value))
        else:
            m.write('%s' % self.upperValue.value)
    if self.taggedValue:
        tvs = ',\n '.join(filter(None, map(getattr, self.taggedValue,
                                     ['value'] * len(self.taggedValue))))
        if tvs:
            m.write(' { %s }' % tvs)
    m.reset()
    mult = m.read()

    return name, mult


def render_property(self, *args, **kwargs):
    """
    Render a gaphor.UML.Property either as an attribute or as a
    (name, multiplicity) tuple for association ends.

    See also: render_attribute, render_association_end
    """
    if self.association:
        return render_association_end(self)
    else:
        return render_attribute(self, *args, **kwargs)


def render_operation(self, visibility=False, type=False, multiplicity=False,
                           default=False, tags=False, direction=False):
    """
    Create a OCL representation of the operation,
    Returns the operation as a string.
    """
    name = self.name
    if not name:
        return ''
    if no_render_pat.match(name):
        return name

    # Render all fields if they all are set to False
    if not (visibility or type or multiplicity or default or tags or direction):
       visibility = type = multiplicity = default = tags = direction = True

    s = StringIO()
    if visibility:
        s.write(vis_map[self.visibility])
        s.write(' ')

    s.write(name)
    s.write('(')

    for p in self.formalParameter:
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
        if p.taggedValue:
             tvs = ', '.join(filter(None, map(getattr, p.taggedValue,
                                              ['value'] * len(p.taggedValue))))
             s.write(' { %s }' % tvs)
        if p is not self.formalParameter[-1]:
            s.write(', ')

    s.write(')')

    rr = self.returnResult and self.returnResult[0]
    if rr:
        if type and rr.typeValue and rr.typeValue.value:
            s.write(': %s' % rr.typeValue.value)
        if multiplicity and rr.upperValue and rr.upperValue.value:  
            if rr.lowerValue and rr.lowerValue.value:
                s.write('[%s..%s]' % (rr.lowerValue.value, rr.upperValue.value))
            else:
                s.write('[%s]' % rr.upperValue.value)
        if rr.taggedValue:
            tvs = ', '.join(filter(None, map(getattr, rr.taggedValue,
                                             ['value'] * len(rr.taggedValue))))
            if tvs:
                s.write(' { %s }' % tvs)
    s.reset()
    return s.read()


def render_lifeline(self):
    """
    """
    return self.name
