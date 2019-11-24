"""
Formatting of UML elements like attributes, operations, stereotypes, etc.
"""

import io
import re
from functools import singledispatch

from gaphor.UML import uml2 as UML


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

    s = io.StringIO()

    if visibility:
        s.write(vis_map[el.visibility])
        s.write(" ")

    if is_derived:
        if el.isDerived:
            s.write("/")

    s.write(name)

    if type and el.typeValue:
        s.write(f": {el.typeValue}")

    if multiplicity and el.upperValue:
        if el.lowerValue:
            s.write(f"[{el.lowerValue}..{el.upperValue}]")
        else:
            s.write(f"[{el.upperValue}]")

    if default and el.defaultValue:
        s.write(f" = {el.defaultValue}")

    if tags:
        slots = []
        for slot in el.appliedStereotype[:].slot:
            if slot:
                slots.append(f"{slot.definingFeature.name}={slot.value}")
        if slots:
            s.write(" { %s }" % ", ".join(slots))
    s.seek(0)
    return s.read()


def format_association_end(el):
    """
    Format association end.
    """
    name = ""
    n = io.StringIO()
    if el.name:
        n.write(vis_map[el.visibility])
        n.write(" ")
        if el.isDerived:
            n.write("/")
        if el.name:
            n.write(el.name)
        n.seek(0)
        name = n.read()

    m = io.StringIO()
    if el.upperValue:
        if el.lowerValue:
            m.write(f"{el.lowerValue}..{el.upperValue}")
        else:
            m.write(f"{el.upperValue}")

    slots = []
    for slot in el.appliedStereotype[:].slot:
        if slot:
            slots.append(format(slot))
    if slots:
        m.write(" { %s }" % ",\n".join(slots))
    m.seek(0)
    mult = m.read()

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

    s = io.StringIO()
    if visibility:
        s.write(vis_map[el.visibility])
        s.write(" ")

    s.write(name)
    s.write("(")

    for p in el.formalParameter:
        s.write(format(p, direction=True, type=True, multiplicity=True, default=True))
        if p is not el.formalParameter[-1]:
            s.write(", ")

    s.write(")")

    rr = el.returnResult and el.returnResult[0]
    if rr:
        if type and rr.typeValue:
            s.write(f": {rr.typeValue}")
        if multiplicity and rr.upperValue:
            if rr.lowerValue:
                s.write(f"[{rr.lowerValue}..{rr.upperValue}]")
            else:
                s.write(f"[{rr.upperValue}]")
        # if rr.taggedValue:
        #    tvs = ', '.join(filter(None, map(getattr, rr.taggedValue,
        #                                     ['value'] * len(rr.taggedValue))))
        #    if tvs:
        #        s.write(' { %s }' % tvs)
    s.seek(0)
    return s.read()


@format.register(UML.Parameter)
def format_parameter(
    el, direction=False, type=False, multiplicity=False, default=False
):
    s = []
    if direction:
        s.append(el.direction)
        s.append(" ")
    s.append(el.name)
    if type and el.typeValue:
        s.append(f": {el.typeValue}")
    if multiplicity and el.upperValue:
        if el.lowerValue:
            s.append(f"[{el.lowerValue}..{el.upperValue}]")
        else:
            s.append(f"[{el.upperValue}]")
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
    return el.name
