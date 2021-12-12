from gaphor.diagram.group import group
from gaphor.UML.uml import Component, UseCase


@group.register(Component, UseCase)
def subsystem_use_case_group(component, usecase):
    """Make subsystem a subject of an use case."""
    usecase.subject = component
    return True
