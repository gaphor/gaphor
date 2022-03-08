from gaphor import UML
from gaphor.diagram.group import group, ungroup


@group.register(UML.Package, UML.Type)
@group.register(UML.Package, UML.Package)
def container_group(parent, element) -> bool:
    """Add Property to a Block."""
    element.package = parent
    return True


@ungroup.register(UML.Package, UML.Type)
@ungroup.register(UML.Package, UML.Package)
def container_ungroup(parent, element) -> bool:
    """Add Property to a Block."""
    if element.package is parent:
        del element.package
        return True
    return False
