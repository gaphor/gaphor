from gaphor import UML
from gaphor.diagram.group import group, ungroup


@group.register(UML.Package, UML.Type)
@group.register(UML.Package, UML.Package)
def container_group(parent, element) -> bool:
    if element.owner:
        ungroup(element.owner, element)

    element.package = parent
    return True


@ungroup.register(UML.Package, UML.Type)
@ungroup.register(UML.Package, UML.Package)
def container_ungroup(parent, element) -> bool:
    if element.package is parent:
        del element.package
        return True
    return False


@group.register(UML.Class, UML.Class)
def class_group(parent, element) -> bool:
    if element.owner:
        ungroup(element.owner, element)
    element.nestingClass = parent
    return True


@ungroup.register(UML.Class, UML.Class)
def class_ungroup(parent, element) -> bool:
    if element.nestingClass is parent:
        del element.nestingClass
        return True
    return False


@group.register(UML.BehavioredClassifier, UML.Behavior)
def behavior_group(parent, element) -> bool:
    if element.owner:
        ungroup(element.owner, element)

    element.behavioredClassifier = parent
    return True


@ungroup.register(UML.BehavioredClassifier, UML.Behavior)
def behavior_ungroup(parent, element) -> bool:
    if element.behavioredClassifier is parent:
        del element.behavioredClassifier
        return True
    return False
