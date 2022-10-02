from gaphor.diagram.group import group, ungroup
from gaphor.UML.uml import Classifier, UseCase


@group.register(Classifier, UseCase)
def subsystem_use_case_group(component, usecase):
    """Make subsystem a subject of a use case."""
    usecase.subject = component
    return True


@ungroup.register(Classifier, UseCase)
def use_case_ungroup(component, usecase):
    """Make subsystem a subject of a use case."""
    if component in usecase.subject:
        usecase.subject.remove(component)
        return True
    return False
