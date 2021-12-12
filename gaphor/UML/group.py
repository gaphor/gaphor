from gaphor import UML
from gaphor.diagram.group import group


@group.register(UML.Package, UML.Type)
@group.register(UML.Package, UML.Package)
def container_group(parent, element) -> bool:
    """Add Property to a Block."""
    element.package = parent
    return True
