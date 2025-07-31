"""The lexical analyzer for attributes and operations.

In this module some parse functions are added for attributes and
operations. The regular expressions are constructed based on a series of
"sub-patterns". This makes it easy to identify the autonomy of an
attribute/operation.
"""

import contextlib

__all__ = ["parse_property", "parse_operation"]

import re

from gaphor.core.format import parse
from gaphor.UML import recipes, uml

# Visibility (optional) ::= '+' | '-' | '#'
vis_subpat = r"\s*(?P<vis>[-+#])?"

# Derived value (optional) ::= [/]
derived_subpat = r"\s*(?P<derived>/)?"

# name (required) ::= name
name_subpat = r"\s*(?P<name>[a-zA-Z_]\w*( +\w+)*)"

# Multiplicity ::= '[' [mult_l ..] mult_u ']'
mult_subpat = r"\s*(?P<has_mult>\[\s*((?P<mult_l>[0-9]+)\s*\.\.)?\s*(?P<mult_u>([0-9]+|\*))?\s*\])?"
multa_subpat = r"\s*(\[?((?P<mult_l>[0-9]+)\s*\.\.)?\s*(?P<mult_u>([0-9]+|\*))\]?)?"

# Type and multiplicity (optional) ::= ':' type
type_subpat = r"\s*(:\s*(?P<type>[a-zA-Z_]\w*( +\w+| *\| *\w+| *<[\w\| ]*>)*))?"

# default value (optional) ::= '=' default
default_subpat = (
    r"\s*(=\s*(?P<default>((?P<oq>[\"'])(?:(?=(?P<ec>\\?))(?P=ec).)*?(?P=oq))|(\S+)))?"
)

# tagged values (optional) ::= '{' tags '}'
tags_subpat = r"\s*(\{\s*(?P<tags>.*?)\s*\})?"

# Parameters (required) ::= '(' [params] ')'
params_subpat = r"\s*\(\s*(?P<params>[^)]+)?\)"

# Possible other parameters (optional) ::= ',' rest
rest_subpat = r"\s*(,\s*(?P<rest>.*))?"

# Direction of a parameter (optional, default in) ::= 'in' | 'out' | 'inout'
dir_subpat = r"\s*((?P<dir>in|out|inout)\s)?"

# A note ::= '#' text
note_subpat = r"\s*(#\s*(?P<note>.*))?"

# Some trailing garbage => no valid syntax...
garbage_subpat = r"\s*(?P<garbage>.*)"


def compile(regex):
    return re.compile(regex, re.MULTILINE | re.DOTALL)


# Attribute:
#   [+-#] [/] name [: type[\[mult\]]] [= default] [{ tagged values }]
attribute_pat = compile(
    r"^"
    + vis_subpat
    + derived_subpat
    + name_subpat
    + type_subpat
    + mult_subpat
    + default_subpat
    + tags_subpat
    + note_subpat
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
    + type_subpat
    + mult_subpat
    + ")?"
    + tags_subpat
    + note_subpat
    + garbage_subpat
)

# Association end multiplicity:
#   [mult] [{ tagged values }]
association_end_mult_pat = compile(
    f"^{vis_subpat}{derived_subpat}{multa_subpat}{tags_subpat}{garbage_subpat}"
)


# Operation:
#   [+|-|#] name ([parameters]) [: type[\[mult\]]] [{ tagged values }]
operation_pat = compile(
    r"^"
    + vis_subpat
    + name_subpat
    + params_subpat
    + type_subpat
    + mult_subpat
    + tags_subpat
    + note_subpat
    + garbage_subpat
)

# One parameter supplied with an operation:
#   [in|out|inout] name [: type[\[mult\]] [{ tagged values }]
parameter_pat = compile(
    r"^"
    + dir_subpat
    + name_subpat
    + type_subpat
    + mult_subpat
    + default_subpat
    + note_subpat
    + garbage_subpat
)

parameters_pat = compile(
    r"^"
    + dir_subpat
    + name_subpat
    + type_subpat
    + mult_subpat
    + default_subpat
    + tags_subpat
    + rest_subpat
)

# Lifeline:
#  [name] [: type]
lifeline_pat = compile(f"^{name_subpat}{type_subpat}{mult_subpat}{garbage_subpat}")


def _set_visibility(el: uml.Feature, vis: str):
    if vis == "#":
        el.visibility = uml.VisibilityKind.protected
    elif vis == "+":
        el.visibility = uml.VisibilityKind.public
    elif vis == "-":
        el.visibility = uml.VisibilityKind.private
    elif vis == "~":
        el.visibility = uml.VisibilityKind.package
    else:
        with contextlib.suppress(AttributeError):
            del el.visibility


def parse_attribute(el: uml.Property, s: str) -> None:
    """Parse string s in the property.

    Tagged values, multiplicity and stuff like that is altered to
    reflect the data in the property string.
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
        if el.note:
            el.note = None
    else:
        g = m.group
        _set_visibility(el, g("vis"))
        el.isDerived = bool(g("derived"))
        el.name = g("name")
        el.typeValue = g("type")
        recipes.set_multiplicity_lower_value(el, g("mult_l"))
        recipes.set_multiplicity_upper_value(el, g("mult_u"))
        if g("has_mult") and not g("mult_u"):
            recipes.set_multiplicity_upper_value(el, "*")
        recipes.set_default_value_from_string(el, g("default"))
        el.note = g("note")


def parse_association_end(el: uml.Property, s: str) -> None:
    """Parse the text at one end of an association.

    The association end holds two strings. It is automatically figured
    out which string is fed to the parser.
    """
    # if no name, then clear as there could be some garbage
    # due to previous parsing (i.e. '[1'
    m = association_end_name_pat.match(s)
    if m and not m.group("name"):
        el.name = None

    # clear also multiplicity if no characters in ``s``
    m = association_end_mult_pat.match(s)
    if m and not m.group("mult_u") and el.upperValue:
        el.upperValue.value = None
        el.upperValue.name = None

    if m and m.group("mult_u") or m.group("tags"):
        g = m.group
        _set_visibility(el, g("vis"))
        el.isDerived = bool(g("derived"))
        recipes.set_multiplicity_lower_value(el, g("mult_l"))
        recipes.set_multiplicity_upper_value(el, g("mult_u"))
    else:
        m = association_end_name_pat.match(s)
        g = m.group
        if g("garbage"):
            el.name = s
            del el.visibility
            del el.isDerived
            del el.note
        else:
            _set_visibility(el, g("vis"))
            el.isDerived = bool(g("derived"))
            el.name = g("name")
            el.note = g("note")
            # Optionally, the multiplicity and tagged values may be defined:
            if g("mult_l"):
                recipes.set_multiplicity_lower_value(el, g("mult_l"))

            if g("mult_u"):
                if not g("mult_l"):
                    recipes.set_multiplicity_lower_value(el, None)
                recipes.set_multiplicity_upper_value(el, g("mult_u"))

            elif g("has_mult") and not g("mult_u"):
                recipes.set_multiplicity_upper_value(el, "*")


@parse.register(uml.NamedElement)
def parse_namedelement(el: uml.NamedElement, text: str) -> None:
    """Parse element by simply assigning text to its name."""
    el.name = text


@parse.register(uml.Property)
def parse_property(el: uml.Property, s: str) -> None:
    if el.association:
        parse_association_end(el, s)
    else:
        parse_attribute(el, s)


@parse.register(uml.Operation)
def parse_operation(el: uml.Operation, s: str) -> None:
    """Parse string s in the operation.

    Tagged values, parameters and visibility is altered to reflect the
    data in the operation string.
    """
    m = operation_pat.match(s)
    if not m or m.group("garbage"):
        el.name = s
        del el.visibility
        for param in list(el.ownedParameter):
            param.unlink()
    else:
        g = m.group
        create = el.model.create
        _set_visibility(el, g("vis"))
        el.name = g("name")
        el.note = g("note")

        defined_params = set()
        if g("type"):
            if returnParameters := [
                p for p in el.ownedParameter if p.direction == "return"
            ]:
                p = returnParameters[0]
            else:
                p = create(uml.Parameter)
                el.ownedParameter = p
                p.direction = "return"
            p.typeValue = g("type")
            recipes.set_multiplicity_lower_value(p, g("mult_l"))
            recipes.set_multiplicity_upper_value(p, g("mult_u"))
            if g("has_mult") and not g("mult_u"):
                recipes.set_multiplicity_upper_value(p, "*")
            defined_params.add(p)

        pindex = 0
        params = g("params")
        while params:
            m = parameters_pat.match(params)
            if not m:
                break
            g = m.group
            try:
                while el.ownedParameter[pindex] in defined_params:
                    pindex += 1
                p = el.ownedParameter[pindex]
            except IndexError:
                p = create(uml.Parameter)
            p.direction = g("dir") or uml.ParameterDirectionKind.in_
            p.name = g("name")
            p.typeValue = g("type")
            recipes.set_multiplicity_lower_value(p, g("mult_l"))
            recipes.set_multiplicity_upper_value(p, g("mult_u"))
            if g("has_mult") and not g("mult_u"):
                recipes.set_multiplicity_upper_value(p, "*")
            recipes.set_default_value_from_string(p, g("default"))
            el.ownedParameter = p
            defined_params.add(p)
            # Do the next parameter:
            params = g("rest")

        # Remove remaining parameters:
        for op in list(el.ownedParameter):
            if op not in defined_params:
                op.unlink()


@parse.register(uml.Parameter)
def parse_parameter(el: uml.Parameter, s: str) -> None:
    m = parameter_pat.match(s)
    if not m or m.group("garbage"):
        el.name = s
        del el.direction
        del el.typeValue
    else:
        g = m.group
        el.direction = g("dir") or "in"
        el.name = g("name")
        el.typeValue = g("type")
        recipes.set_multiplicity_lower_value(el, g("mult_l"))
        recipes.set_multiplicity_upper_value(el, g("mult_u"))
        if g("has_mult") and not g("mult_u"):
            recipes.set_multiplicity_upper_value(el, "*")
        recipes.set_default_value_from_string(el, g("default"))


def parse_lifeline(el: uml.Lifeline, s: str) -> None:
    """Parse string s in a lifeline.

    If a class is defined and can be found in the datamodel, then a
    class is connected to the lifelines 'represents' property.
    """
    m = lifeline_pat.match(s)
    g = m.group
    if not m or g("garbage"):
        el.name = s
    else:
        el.name = g("name") + ": "
        if t := g("type"):
            el.name += f": {t}"
        # In the near future the data model should be extended with
        # Lifeline.represents: ConnectableElement


def render_lifeline(el: uml.Lifeline) -> str:
    return el.name or ""
