#!/usr/bin/env python
# vim:sw=4:et
"""Lexical analizer for attributes and operations.

In this module some parse functions are added for attributes and operations.
The regular expressions are constructed based on a series of
"sub-patterns". This makes it easy to identify the autonomy of an
attribute/operation.
"""

__all__ = [ 'parse_attribute', 'parse_operation' ]

import re
import gaphor

# Visibility (optional) ::= '+' | '-' | '#'
vis_subpat = r'\s*(?P<vis>[-+#])?'

# Derived value (optional) ::= [/]
derived_subpat = r'\s*(?P<derived>/)?'

# name (required) ::= name
name_subpat = r'\s*(?P<name>\w+)'

# Multiplicity (added to type_subpat) ::= '[' [mult_l ..] mult_u ']'
mult_subpat = r'\s*(\[\s*((?P<mult_l>[0-9]+)\s*\.\.)?\s*(?P<mult_u>([0-9]+|\*))\s*\])?'

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
dir_subpat = r'\s*(?P<dir>in|out|inout)?'

# Some trailing garbage => no valid syntax...
garbage_subpat = r'\s*(?P<garbage>.*)'

# Property:
#   [+-#] [/] name [: type[\[mult\]]] [= default] [{ tagged values }]
property_pat = re.compile(r'^' + vis_subpat + derived_subpat + name_subpat + type_subpat + default_subpat + tags_subpat + garbage_subpat)

# Operation:
#   [+|-|#] name ([parameters]) [: type[\[mult\]]] [{ tagged values }]
operation_pat = re.compile(r'^' + vis_subpat + name_subpat + params_subpat + type_subpat + tags_subpat + garbage_subpat)

# One parameter supplied with an operation:
#   [in|out|inout] name [: type[\[mult\]] [{ tagged values }]
parameter_pat = re.compile(r'^' + dir_subpat + name_subpat + type_subpat + default_subpat + tags_subpat + rest_subpat)


def parse_attribute(self, s, element_factory=None):
    """Parse string s in the property. Tagged values, multiplicity and stuff
    like that is altered to reflect the data in the property string.
    """
    m = property_pat.match(s)
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
        if self.taggedValue:
            self.taggedValue.value = None
    else:
        from uml2 import LiteralString
        if not element_factory:
            element_factory = gaphor.resource("ElementFactory")
        vis = g('vis')
        if vis == '+':
            self.visibility = 'public'
        elif vis == '#':
            self.visibility = 'protected'
        elif vis == '-':
            self.visibility = 'private'
        else:
            try:
                del self.visibility
            except AttributeError:
                pass
        self.isDerived = g('derived') and True or False
        self.name = g('name')
        if not self.typeValue:
            self.typeValue = element_factory.create(LiteralString)
        self.typeValue.value = g('type')
        if not self.lowerValue:
            self.lowerValue = element_factory.create(LiteralString)
        self.lowerValue.value = g('mult_l')
        if not self.upperValue:
            self.upperValue = element_factory.create(LiteralString)
        self.upperValue.value = g('mult_u')
        if not self.defaultValue:
            self.defaultValue = element_factory.create(LiteralString)
        self.defaultValue.value = g('default')
        if not self.taggedValue:
            self.taggedValue = element_factory.create(LiteralString)
        self.taggedValue.value = g('tags')
        #print g('vis'), g('derived'), g('name'), g('type'), g('mult_l'), g('mult_u'), g('default'), g('tags')


def parse_operation(self, s, element_factory=None):
    """Parse string s in the operation. Tagged values, parameters and
    visibility is altered to reflect the data in the operation string.
    """
    m = operation_pat.match(s)
    g = m.group
    if not m or g('garbage'):
        self.name = s
        del self.visibility
        if self.returnResult:
            self.returnResult.unlink()
        if self.formalParameter:
            self.formalParameter.unlink()
    else:
        from uml2 import Parameter, LiteralString
        if not element_factory:
            element_factory = gaphor.resource("ElementFactory")
        vis = g('vis')
        if vis == '+':
            self.visibility = 'public'
        elif vis == '#':
            self.visibility = 'protected'
        elif vis == '-':
            self.visibility = 'private'
        else:
            try:
                del self.visibility
            except AttributeError:
                pass
        self.name = g('name')
        if not self.returnResult:
            self.returnResult = element_factory.create(Parameter)
        p = self.returnResult[0]
        p.direction = 'return'
        if not p.typeValue:
            p.typeValue = element_factory.create(LiteralString)
        p.typeValue.value = g('type')
        if not p.lowerValue:
            p.lowerValue = element_factory.create(LiteralString)
        p.lowerValue.value = g('mult_l')
        if not p.upperValue:
            p.upperValue = element_factory.create(LiteralString)
        p.upperValue.value = g('mult_u')
        # FIXME: Maybe add to Operation.ownedRule?
        if not p.taggedValue:
            p.taggedValue = element_factory.create(LiteralString)
        p.taggedValue.value = g('tags')
        #print g('vis'), g('name'), g('type'), g('mult_l'), g('mult_u'), g('tags')
        
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
                p = element_factory.create(Parameter)
            p.direction = g('dir') or 'in'
            p.name = g('name')
            if not p.typeValue:
                p.typeValue = element_factory.create(LiteralString)
            p.typeValue.value = g('type')
            if not p.lowerValue:
                p.lowerValue = element_factory.create(LiteralString)
            p.lowerValue.value = g('mult_l')
            if not p.upperValue:
                p.upperValue = element_factory.create(LiteralString)
            p.upperValue.value = g('mult_u')
            if not p.defaultValue:
                p.defaultValue = element_factory.create(LiteralString)
            p.defaultValue.value = g('default')
            if not p.taggedValue:
                p.taggedValue = element_factory.create(LiteralString)
            p.taggedValue.value = g('tags')
            self.formalParameter = p

            #print ' ', g('dir') or 'in', g('name'), g('type'), g('mult_l'), g('mult_u'), g('default'), g('tags')

            # Do the next parameter:
            params = g('rest')
            pindex += 1

        # Remove remaining parameters:
        for fp in self.formalParameter[pindex:]:
            fp.unlink()

