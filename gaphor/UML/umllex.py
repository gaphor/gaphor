"""
The lexical analyzer for attributes and operations.

In this module some parse functions are added for attributes and operations.
The regular expressions are constructed based on a series of
"sub-patterns". This makes it easy to identify the autonomy of an
attribute/operation.
"""

__all__ = ["parse_property", "parse_operation"]

import re
from functools import singledispatch

from gaphor.UML import uml


@singledispatch
def parse(el, text):
    """
    Parser for an UML element.
    """
    raise NotImplementedError(
        "Parsing routine for type %s not implemented yet" % type(el)
    )


# Visibility (optional) ::= '+' | '-' | '#'
vis_subpat = r"\s*(?P<vis>[-+#])?"

# Derived value (optional) ::= [/]
derived_subpat = r"\s*(?P<derived>/)?"

# name (required) ::= name
name_subpat = r"\s*(?P<name>[a-zA-Z_]\w*)"

# Multiplicity (added to type_subpat) ::= '[' [mult_l ..] mult_u ']'
mult_subpat = r"\s*(\[\s*((?P<mult_l>[0-9]+)\s*\.\.)?\s*(?P<mult_u>([0-9]+|\*))\s*\])?"
multa_subpat = r"\s*(\[?((?P<mult_l>[0-9]+)\s*\.\.)?\s*(?P<mult_u>([0-9]+|\*))\]?)?"

# Type and multiplicity (optional) ::= ':' type [mult]
type_subpat = r"\s*(:\s*(?P<type>\w+)\s*" + mult_subpat + r")?"

# default value (optional) ::= '=' default
default_subpat = r"\s*(=\s*(?P<default>\S+))?"

# tagged values (optional) ::= '{' tags '}'
tags_subpat = r"\s*(\{\s*(?P<tags>.*?)\s*\})?"

# Parameters (required) ::= '(' [params] ')'
params_subpat = r"\s*\(\s*(?P<params>[^)]+)?\)"

# Possible other parameters (optional) ::= ',' rest
rest_subpat = r"\s*(,\s*(?P<rest>.*))?"

# Direction of a parameter (optional, default in) ::= 'in' | 'out' | 'inout'
dir_subpat = r"\s*((?P<dir>in|out|inout)\s)?"

# Some trailing garbage => no valid syntax...
garbage_subpat = r"\s*(?P<garbage>.*)"


def compile(regex):
    return re.compile(regex, re.MULTILINE | re.S)


# Attribute:
#   [+-#] [/] name [: type[\[mult\]]] [= default] [{ tagged values }]
attribute_pat = compile(
    r"^"
    + vis_subpat
    + derived_subpat
    + name_subpat
    + type_subpat
    + default_subpat
    + tags_subpat
    + garbage_subpat
)

# Association end name:
#   [[+-#] [/] name [\[mult\]]] [{ tagged values }]
association_end_name_pat = compile(
    r"^"
    + "("
    + vis_subpat
    + derived_subpat
    + name_subpat
    + mult_subpat
    + ")?"
    + tags_subpat
    + garbage_subpat
)

# Association end multiplicity:
#   [mult] [{ tagged values }]
association_end_mult_pat = compile(r"^" + multa_subpat + tags_subpat + garbage_subpat)

# Operation:
#   [+|-|#] name ([parameters]) [: type[\[mult\]]] [{ tagged values }]
operation_pat = compile(
    r"^"
    + vis_subpat
    + name_subpat
    + params_subpat
    + type_subpat
    + tags_subpat
    + garbage_subpat
)

# One parameter supplied with an operation:
#   [in|out|inout] name [: type[\[mult\]] [{ tagged values }]
parameter_pat = compile(
    r"^"
    + dir_subpat
    + name_subpat
    + type_subpat
    + default_subpat
    + tags_subpat
    + rest_subpat
)

# Lifeline:
#  [name] [: type]
lifeline_pat = compile("^" + name_subpat + type_subpat + garbage_subpat)


def _set_visibility(el: uml.Feature, vis: str):
    if vis == "+":
        el.visibility = "public"
    elif vis == "#":
        el.visibility = "protected"
    elif vis == "~":
        el.visibility = "package"
    elif vis == "-":
        el.visibility = "private"
    else:
        try:
            del el.visibility
        except AttributeError:
            pass


def parse_attribute(el: uml.Property, s: str) -> None:
    """
    Parse string s in the property. Tagged values, multiplicity and stuff
    like that is altered to reflect the data in the property string.
    """
    m = attribute_pat.match(s)
    if not m or m.group("garbage"):
        el.name = s
        del el.visibility
        del el.isDerived
        if el.typeValue:
            el.typeValue = None
        if el.lowerValue:
            el.lowerValue = None
        if el.upperValue:
            el.upperValue = None
        if el.defaultValue:
            el.defaultValue = None
    else:
        g = m.group
        _set_visibility(el, g("vis"))
        el.isDerived = g("derived") and True or False
        el.name = g("name")
        el.typeValue = g("type")
        el.lowerValue = g("mult_l")
        el.upperValue = g("mult_u")
        el.defaultValue = g("default")


def parse_association_end(el: uml.Property, s: str) -> None:
    """
    Parse the text at one end of an association. The association end holds
    two strings. It is automatically figured out which string is fed to the
    parser.
    """
    el.model.create

    # if no name, then clear as there could be some garbage
    # due to previous parsing (i.e. '[1'
    m = association_end_name_pat.match(s)
    if m and not m.group("name"):
        el.name = None

    # clear also multiplicity if no characters in ``s``
    m = association_end_mult_pat.match(s)
    if m and not m.group("mult_u") and el.upperValue:
        el.upperValue = None

    if m and m.group("mult_u") or m.group("tags"):
        g = m.group
        el.lowerValue = g("mult_l")
        el.upperValue = g("mult_u")
    else:
        m = association_end_name_pat.match(s)
        g = m.group
        if g("garbage"):
            el.name = s
            del el.visibility
            del el.isDerived
        else:
            _set_visibility(el, g("vis"))
            el.isDerived = g("derived") and True or False
            el.name = g("name")
            # Optionally, the multiplicity and tagged values may be defined:
            if g("mult_l"):
                el.lowerValue = g("mult_l")

            if g("mult_u"):
                if not g("mult_l"):
                    el.lowerValue = None
                el.upperValue = g("mult_u")


@parse.register(uml.Property)
def parse_property(el: uml.Property, s: str) -> None:
    if el.association:
        parse_association_end(el, s)
    else:
        parse_attribute(el, s)


@parse.register(uml.Operation)
def parse_operation(el: uml.Operation, s: str) -> None:
    """
    Parse string s in the operation. Tagged values, parameters and
    visibility is altered to reflect the data in the operation string.
    """
    m = operation_pat.match(s)
    if not m or m.group("garbage"):
        el.name = s
        del el.visibility
        list(map(uml.Parameter.unlink, list(el.returnResult)))
        list(map(uml.Parameter.unlink, list(el.formalParameter)))
    else:
        g = m.group
        create = el.model.create
        _set_visibility(el, g("vis"))
        el.name = g("name")
        if not el.returnResult:
            el.returnResult = create(uml.Parameter)
        p = el.returnResult[0]
        p.direction = "return"
        p.typeValue = g("type")
        p.lowerValue = g("mult_l")
        p.upperValue = g("mult_u")

        pindex = 0
        params = g("params")
        while params:
            m = parameter_pat.match(params)
            if not m:
                break
            g = m.group
            try:
                p = el.formalParameter[pindex]
            except IndexError:
                p = create(uml.Parameter)
            p.direction = g("dir") or "in"
            p.name = g("name")
            p.typeValue = g("type")
            p.lowerValue = g("mult_l")
            p.upperValue = g("mult_u")
            p.defaultValue = g("default")
            el.formalParameter = p

            # Do the next parameter:
            params = g("rest")
            pindex += 1

        # Remove remaining parameters:
        for fp in el.formalParameter[pindex:]:
            fp.unlink()


def parse_lifeline(el: uml.Lifeline, s: str) -> None:
    """
    Parse string s in a lifeline. If a class is defined and can be found
    in the datamodel, then a class is connected to the lifelines 'represents'
    property.
    """
    m = lifeline_pat.match(s)
    g = m.group
    if not m or g("garbage"):
        el.name = s
    else:
        el.name = g("name") + ": "
        t = g("type")
        if t:
            el.name += ": " + t
        # In the near future the data model should be extended with
        # Lifeline.represents: ConnectableElement


def render_lifeline(el: uml.Lifeline) -> str:
    """
    """
    return el.name or ""


@parse.register(uml.NamedElement)
def parse_namedelement(el: uml.NamedElement, text: str) -> None:
    """
    Parse named element by simply assigning text to its name.
    """
    el.name = text
