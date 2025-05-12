"""Formatting of UML elements like attributes, operations, stereotypes, etc."""

import re

from gaphor.core.format import format
from gaphor.i18n import gettext
from gaphor.UML import recipes
from gaphor.UML import uml as UML


@format.register(UML.NamedElement)
def format_namedelement(el: UML.NamedElement, **kwargs):
    return el.name or ""


@format.register(UML.Relationship)
def format_relationship(el):
    return el.__class__.__name__


@format.register(UML.Dependency)
def format_dependency(el):
    return gettext("supplier: {name}").format(
        name=len(el.supplier) > 0 and el.supplier[0].name or ""
    )


# Do not render if the name still contains a visibility element
no_render_pat = re.compile(r"^\s*[+#-]", re.MULTILINE | re.DOTALL)
vis_map = {"public": "+", "protected": "#", "package": "~", "private": "-"}


@format.register
def format_property(
    el: UML.Property,
    visibility=False,
    is_derived=False,
    type=False,
    multiplicity=False,
    default=False,
    tags=False,
    note=False,
):
    """Create an OCL representation of the attribute, Returns the attribute as
    a string. If one or more of the parameters (visibility, is_derived, type,
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
        if el.type and el.type.name:
            s.append(f": {el.type.name}")
        elif el.typeValue:
            s.append(f": {el.typeValue}")

    if multiplicity:
        s.append(format_multiplicity(el))

    if default and el.defaultValue:
        default_value = recipes.get_literal_value_as_string(el.defaultValue)
        if default_value:
            s.append(f" = {default_value}")

    if tags:
        tag_vals = []
        if el.isReadOnly:
            tag_vals.append(gettext("readOnly"))
        tag_vals.extend(format(slot) for slot in el.appliedStereotype[:].slot if slot)

        if tag_vals:
            s.append(f" {{ {', '.join(tag_vals)} }}")

    if note and el.note:
        s.append(f" # {el.note}")

    return "".join(s)


def format_association_end(el) -> tuple[str, str]:
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
        m.append(" {{ {} }}".format(",\n".join(slots)))
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
    """Create an OCL representation of the operation, Returns the operation as
    a string."""
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

    if type:
        if el.type and el.type.name:
            s.append(f": {el.type.name}")
        elif el.typeValue:
            s.append(f": {el.typeValue}")

    if multiplicity:
        s.append(format_multiplicity(el))

    if default and el.defaultValue and el.defaultValue.value:
        s.append(f" = {recipes.get_literal_value_as_string(el.defaultValue)}")
    return "".join(s)


@format.register(UML.Slot)
def format_slot(el):
    return f'{el.definingFeature.name} = "{el.value.value}"' if el.value else ""


@format.register(UML.Pin)
def format_pin(el, **kwargs):
    if not el:
        return ""

    s = [el.name or ""]

    if el.type and el.type.name:
        s.append(f": {el.type.name}")

    if el.upperValue or el.lowerValue:
        s.append(format_multiplicity(el))

    return "".join(s)


@format.register(UML.MultiplicityElement)
def format_multiplicity(el, bare=False):
    m = ""
    upper_value_string = recipes.get_multiplicity_upper_value_as_string(el)
    lower_value_string = recipes.get_multiplicity_lower_value_as_string(el)
    if el.upperValue and upper_value_string is not None:
        m = (
            f"{lower_value_string}..{upper_value_string}"
            if el.lowerValue and lower_value_string is not None
            else f"{upper_value_string}"
        )
    return f"[{m}]" if m and not bare else m


@format.register(UML.Generalization)
def format_generalization(el):
    return gettext("general: {name}").format(name=el.general and el.general.name or "")


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


@format.register(UML.CallBehaviorAction)
def format_call_behavior_action_name(el):
    """Name conforms to UML2.5.1 16.3.4.1 naming description"""
    return el.behavior.name if el.behavior and not el.name else el.name or ""


@format.register(UML.ActivityParameterNode)
def format_activity_parameter_node_name(
    el, direction=False, type=False, multiplicity=False, default=False
):
    if el.parameter is None:
        return ""
    return format_parameter(el.parameter, direction, type, multiplicity, default)
