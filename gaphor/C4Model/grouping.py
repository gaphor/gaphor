from gaphor.C4Model.diagramitems import C4ContainerDatabaseItem, C4ContainerItem
from gaphor.diagram.grouping import AbstractGroup, Group
from gaphor.UML.modelfactory import owner_package


@Group.register(C4ContainerItem, C4ContainerItem)
@Group.register(C4ContainerItem, C4ContainerDatabaseItem)
class ContainerGroup(AbstractGroup):
    """Add Property to a Block."""

    def can_contain(self) -> bool:
        return True

    def group(self):
        self.item.subject.package = self.parent.subject

    def ungroup(self):
        self.item.subject.package = owner_package(self.item.diagram.owner)
