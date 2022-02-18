from gaphor.diagram.grouping import AbstractGroup, Group
from gaphor.UML.classes.component import ComponentItem
from gaphor.UML.usecases.usecase import UseCaseItem


@Group.register(ComponentItem, UseCaseItem)
class SubsystemUseCaseGroup(AbstractGroup):
    """Make subsystem a subject of an use case."""

    def group(self):
        component = self.parent.subject
        usecase = self.item.subject
        usecase.subject = component

    def ungroup(self):
        component = self.parent.subject
        usecase = self.item.subject
        usecase.subject.remove(component)
