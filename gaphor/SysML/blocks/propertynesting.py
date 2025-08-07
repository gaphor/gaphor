from __future__ import annotations

from gi.repository import GLib

from gaphor import UML
from gaphor.diagram.group import group, ungroup


def _par_pairs(parent_el: UML.Property, elem_el: UML.Property):
    """Yield (parent_item, child_item) pairs that share the same Parametric
    Diagram (diagramType == 'par')."""
    parent_pres = list(getattr(parent_el, "presentation", []))
    elem_pres = list(getattr(elem_el, "presentation", []))

    for ep in elem_pres:
        d = getattr(ep, "diagram", None)
        if getattr(d, "diagramType", None) != "par":
            continue
        for pp in parent_pres:
            if getattr(pp, "diagram", None) is d:
                yield pp, ep


def _refresh(item):
    try:
        # PropertyItem.request_update() will recount children and rebuild shape
        item.request_update()
    except Exception:
        pass
    return False  # stop idle


@group.register(UML.Property, UML.Property)
def group_property_under_property(parent: UML.Property, element: UML.Property) -> bool:
    """
    Visual nesting of properties, but only on Parametric Diagrams.
    """
    pairs = list(_par_pairs(parent, element))
    if not pairs:
        return False  # not a Parametric Diagram -> no nesting

    # Reparenting is handled by the framework. After that, refresh new and old
    # parents so spacers appear/disappear correctly.
    for new_parent_item, child_item in pairs:
        old_parent_item = getattr(child_item, "parent", None)
        if isinstance(getattr(old_parent_item, "subject", None), UML.Property):
            GLib.idle_add(_refresh, old_parent_item)
        GLib.idle_add(_refresh, new_parent_item)

    return True  # diagram-only reparenting


@group.register(UML.Diagram, UML.Property)
def group_property_to_diagram_root(diagram: UML.Diagram, element: UML.Property) -> bool:
    """
    De-nesting by dropping a property to the diagram background (root).
    Only act on Parametric Diagrams to keep behavior scoped.
    """
    if getattr(diagram, "diagramType", None) != "par":
        return False

    for ep in list(getattr(element, "presentation", [])):
        if getattr(ep, "diagram", None) is diagram:
            old_parent_item = getattr(ep, "parent", None)
            if isinstance(getattr(old_parent_item, "subject", None), UML.Property):
                GLib.idle_add(_refresh, old_parent_item)
            break

    return True


@ungroup.register(UML.Property, UML.Property)
def ungroup_property_from_property(parent: UML.Property, element: UML.Property) -> bool:
    """
    If explicit ungroup is used, refresh parent(s) on Parametric Diagrams.
    """
    for parent_item, _ in _par_pairs(parent, element):
        GLib.idle_add(_refresh, parent_item)
    return True
