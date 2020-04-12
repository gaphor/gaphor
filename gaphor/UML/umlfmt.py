"""
Formatting of UML elements like attributes, operations, stereotypes, etc.
"""

import re
from functools import singledispatch

from gaphor.UML import uml as UML


@singledispatch
def format(el):
    """
    Format an UML element.
    """
    raise NotImplementedError(
        "Format routine for type %s not implemented yet" % type(el)
    )


@format.register(UML.Property)
def format_property(el, *args, **kwargs):
    """
    Format property or an association end.
    """
    if el.association and not (args or kwargs):
        return format_association_end(el)
    else:
        return format_attribute(el, *args, **kwargs)


def compile(regex):
    return re.compile(regex, re.MULTILINE | re.S)


# Do not render if the name still contains a visibility element
no_render_pat = compile(r"^\s*[+#-]")
vis_map = {"public": "+", "protected": "#", "package": "~", "private": "-"}


def format_attribute(
    el,
    visibility=False,
    is_derived=False,
    type=False,
    multiplicity=False,
    default=False,
    tags=False,
):
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
        return name

    if no_render_pat.match(name):
        return name

    # Render all fields if they all are set to False
    if not (visibility or is_derived or type or multiplicity or default):
        visibility = is_derived = type = multiplicity = default = True

    s = []

    if visibility:
        s.append(vis_map[el.visibility])
        s.append(" ")

    if is_derived and el.isDerived:
        s.append("/")

    s.append(name)

    if type and el.typeValue:
        s.append(f": {el.typeValue}")

    if multiplicity:
        s.append(format_multiplicity(el))

    if default and el.defaultValue:
        s.append(f" = {el.defaultValue}")

    if tags:
        slots = [format(slot) for slot in el.appliedStereotype[:].slot if slot]
        if slots:
            s.append(" { %s }" % ", ".join(slots))
    return "".join(s)


def format_association_end(el):
    """
    Format association end.
    """
    name = ""
    n = []
    if el.name:
        n.append(vis_map[el.visibility])
        n.append(" ")
        if el.isDerived:
            n.append("/")
        if el.name:
            n.append(el.name)

        name = "".join(n)

    m = []
    m.append(format_multiplicity(el, bare=True))

    slots = [format(slot) for slot in el.appliedStereotype[:].slot if slot]
    if slots:
        m.append(" { %s }" % ",\n".join(slots))
    mult = "".join(m)

    return name, mult


@format.register(UML.Operation)
def format_operation(
    el,
    pattern=None,
    visibility=False,
    type=False,
    multiplicity=False,
    default=False,
    tags=False,
    direction=False,
):
    """
    Create a OCL representation of the operation,
    Returns the operation as a string.
    """
    name = el.name
    if not name:
        return ""
    if no_render_pat.match(name):
        return name

    # Render all fields if they all are set to False
    if not (visibility or type or multiplicity or default or tags or direction):
        visibility = type = multiplicity = default = tags = direction = True

    s = []
    if visibility:
        s.append(f"{vis_map[el.visibility]} ")

    s.append(name)
    s.append("(")

    for p in el.formalParameter:
        s.append(
            format(
                p,
                direction=direction,
                type=type,
                multiplicity=multiplicity,
                default=default,
            )
        )
        if p is not el.formalParameter[-1]:
            s.append(", ")

    s.append(")")

    rr = el.returnResult and el.returnResult[0]
    if rr:
        s.append(format(rr, type=type, multiplicity=multiplicity, default=default))
    return "".join(s)


@format.register(UML.Parameter)
def format_parameter(
    el, direction=False, type=False, multiplicity=False, default=False
):
    s = []
    if direction:
        s.append(f"{el.direction} ")

    s.append(el.name or "")

    if type and el.typeValue:
        s.append(f": {el.typeValue}")

    if multiplicity:
        s.append(format_multiplicity(el))

    if default and el.defaultValue:
        s.append(f" = {el.defaultValue}")
    # if p.taggedValue:
    #     tvs = ', '.join(filter(None, map(getattr, p.taggedValue,
    #                                      ['value'] * len(p.taggedValue))))
    #     s.append(' { %s }' % tvs)
    return "".join(s)


@format.register(UML.Slot)
def format_slot(el):
    return f'{el.definingFeature.name} = "{el.value}"'


@format.register(UML.NamedElement)
def format_namedelement(el):
    """
    Format named element.
    """
    return el.name or ""


def format_multiplicity(el, bare=False):
    m = ""
    if el.upperValue:
        m = f"{el.lowerValue}..{el.upperValue}" if el.lowerValue else f"{el.upperValue}"
    return f"[{m}]" if m and not bare else m
