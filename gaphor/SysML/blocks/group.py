from gi.repository import GLib

from gaphor import UML
from gaphor.diagram.group import group, ungroup
from gaphor.SysML.sysml import Block
from gaphor.UML import Property


def _refresh_property_item(item):
    try:
        if hasattr(item, "request_update"):
            item.request_update()
    except Exception:
        pass
    return False


@group.register(Block, Property)
def block_property_group(parent, element):
    """Add Property to a Block.

    - On Parametric Diagrams ('par'): purely visual (no model change).
      Also refresh an old Property parent so its spacer disappears.
    - Otherwise: keep original model behavior.
    """
    # Check for Parametric Diagram context
    for ep in list(getattr(element, "presentation", [])):
        d = getattr(ep, "diagram", None)
        if getattr(d, "diagramType", None) == "par":
            # Visual-only: do not change model ownership
            old_parent_item = getattr(ep, "parent", None)
            if isinstance(getattr(old_parent_item, "subject", None), UML.Property):
                GLib.idle_add(_refresh_property_item, old_parent_item)
            return True

    # Original behavior (non-parametric diagrams)
    if element.association:
        return element.owner is parent

    parent.ownedAttribute = element
    return True


@ungroup.register(Block, Property)
def property_ungroup(parent, element):
    if not element.association and element in parent.ownedAttribute:
        del parent.ownedAttribute[element]
        return True
    return False
