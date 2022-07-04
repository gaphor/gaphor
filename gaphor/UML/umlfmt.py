"""Formatting of UML elements like attributes, operations, stereotypes, etc."""

import re
from typing import Tuple

from gaphor.core import gettext
from gaphor.core.format import format
from gaphor.UML import uml as UML

# Do not render if the name still contains a visibility element
no_render_pat = re.compile(r"^\s*[+#-]", re.MULTILINE | re.S)
vis_map = {"public": "+", "protected": "#", "package": "~", "private": "-"}


@format.register(UML.Property)
def format_property(
    el,
    visibility=False,
    is_derived=False,
    type=False,
    multiplicity=False,
    default=False,
    tags=False,
    note=False,
):
    """Create a OCL representation of the attribute, Returns the attribute as a
    string. If one or more of the parameters (visibility, is_derived, type,
    multiplicity, default and/or tags) is set, only that field is rendered.
    Note that the name of the attribute is always rendered, so a parseable
    string is returned.

    Note that, when some of those parameters are set, parsing the string
    will not give you the same result.
    """
    name = el.name

    if name and no_render_pat.match(name):
        return name

    # Render all fields if they all are set to False
    if not (visibility or is_derived or type or multiplicity or default):
        visibility = is_derived = type = multiplicity = default = True

    s: list[str] = []

    if name:
        if visibility:
            s.extend((vis_map[el.visibility], " "))
        if is_derived and el.isDerived:
            s.append("/")

        s.append(name)

    if type:
        if el.typeValue:
            s.append(f": {el.typeValue}")
        elif el.type and el.type.name:
            s.append(f": {el.type.name}")

    if multiplicity:
        s.append(format_multiplicity(el))

    if default and el.defaultValue:
        s.append(f" = {el.defaultValue}")

    if tags and (
        slots := [format(slot) for slot in el.appliedStereotype[:].slot if slot]
    ):
        s.append(" { %s }" % ", ".join(slots))

    if note and el.note:
        s.append(f" # {el.note}")

    return "".join(s)


def format_association_end(el) -> Tuple[str, str]:
    """Format association end."""
    name = ""
    if el.name:
        n = [vis_map[el.visibility], " "]
        if el.isDerived:
            n.append("/")
        n.append(el.name)

        name = "".join(n)

    m = [format_multiplicity(el, bare=True)]
    if slots := [format(slot) for slot in el.appliedStereotype[:].slot if slot]:
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
    note=False,
):
    """Create a OCL representation of the operation, Returns the operation as a
    string."""
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

    s.extend(
        (
            name,
            "(",
            ", ".join(
                format(
                    p,
                    direction=direction,
                    type=type,
                    multiplicity=multiplicity,
                    default=default,
                )
                for p in el.ownedParameter
                if p.direction != "return"
            ),
            ")",
        )
    )

    if rr := next((p for p in el.ownedParameter if p.direction == "return"), None):
        s.append(format(rr, type=type, multiplicity=multiplicity, default=default))

    if note and el.note:
        s.append(f" # {el.note}")

    return "".join(s)


@format.register(UML.Parameter)
def format_parameter(
    el, direction=False, type=False, multiplicity=False, default=False
):
    if not (direction or type or multiplicity or default):
        direction = type = multiplicity = default = True

    s = []
    name = el.name
    if name and direction:
        s.append(f"{el.direction} ")

    s.append(name or "")

    if type and el.typeValue:
        s.append(f": {el.typeValue}")

    if multiplicity:
        s.append(format_multiplicity(el))

    if default and el.defaultValue:
        s.append(f" = {el.defaultValue}")
    return "".join(s)


@format.register(UML.Slot)
def format_slot(el):
    return f'{el.definingFeature.name} = "{el.value}"'


@format.register(UML.NamedElement)
def format_namedelement(el, **kwargs):
    """Format named element."""
    return el.name or ""


@format.register(UML.MultiplicityElement)
def format_multiplicity(el, bare=False):
    m = ""
    if el.upperValue:
        m = f"{el.lowerValue}..{el.upperValue}" if el.lowerValue else f"{el.upperValue}"
    return f"[{m}]" if m and not bare else m


@format.register(UML.Relationship)
def format_relationship(el):
    return el.__class__.__name__


@format.register(UML.Generalization)
def format_generalization(el):
    return gettext("general: {name}").format(name=el.general and el.general.name or "")


@format.register(UML.Dependency)
def format_dependency(el):
    return gettext("supplier: {name}").format(
        name=el.supplier and el.supplier.name or ""
    )


@format.register(UML.Extend)
def format_extend(el):
    return gettext("extend: {name}").format(
        name=el.extendedCase and el.extendedCase.name or ""
    )


@format.register(UML.Include)
def format_include(el):
    return gettext("include: {name}").format(
        name=el.addition and el.addition.name or ""
    )
