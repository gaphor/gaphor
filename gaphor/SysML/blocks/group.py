from gaphor.diagram.group import group, ungroup
from gaphor.SysML.sysml import Block, Property


@group.register(Block, Property)
def block_property_group(parent, element):
    """Add Property to a Block."""

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
