import gaphor.UML.uml as UML
from gaphor.diagram.group import Root, group, owner, owns, ungroup


@owner.register
def _(element: UML.Element):
    if not element.owner and isinstance(element, UML.MultiplicityElement):
        return None

    return element.owner or Root


@owner.register
def _(element: UML.NamedElement):
    return (
        element.owner
        or element.memberNamespace
        or (None if isinstance(element, UML.MultiplicityElement) else Root)
    )


@owner.register
def _(element: UML.StructuralFeature):
    if not (element.owner or element.memberNamespace):
        return None

    return element.owner or element.memberNamespace


@owner.register
def _(
    _element: UML.Slot
    | UML.Comment
    | UML.Image
    | UML.InstanceSpecification
    | UML.OccurrenceSpecification
    | UML.ValueSpecification,
):
    return None


@owns.register
def _(element: UML.Element):
    return [e for e in element.ownedElement if e.owner is element and owner(e)] + (
        [
            e
            for e in element.member
            if e.memberNamespace is element and not e.owner and owner(e)
        ]
        if isinstance(element, UML.Namespace)
        else []
    )


@group.register(UML.Element, UML.Diagram)
def diagram_group(element, diagram):
    diagram.element = element
    return True


@ungroup.register(UML.Element, UML.Diagram)
def diagram_ungroup(element, diagram):
    if diagram.element is element:
        del diagram.element
        return True
    return False


@group.register(UML.Package, UML.PackageableElement)
def packageable_element_group(
    parent: UML.Package, element: UML.PackageableElement
) -> bool:
    if element.owner:
        ungroup(element.owner, element)

    element.owningPackage = parent
    return True


@ungroup.register(UML.Package, UML.PackageableElement)
def packageable_element_ungroup(
    parent: UML.Package, element: UML.PackageableElement
) -> bool:
    if element.owningPackage is parent:
        del element.owningPackage
        return True
    return False


@group.register(UML.Package, UML.Type)
def container_group(parent, element) -> bool:
    if element.owner:
        ungroup(element.owner, element)
    element.owningPackage = parent
    element.package = parent
    return True


@ungroup.register(UML.Package, UML.Type)
def container_ungroup(parent, element) -> bool:
    if element.package is parent:
        del element.owningPackage
        del element.package
        return True
    return False


@group.register(UML.Package, UML.Package)
def package_group(parent, element) -> bool:
    if element.owner:
        ungroup(element.owner, element)
    element.nestingPackage = parent
    return True


@ungroup.register(UML.Package, UML.Package)
def package_ungroup(parent, element) -> bool:
    if element.nestingPackage is parent:
        del element.nestingPackage
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


@group.register(UML.Artifact, UML.Property)
@group.register(UML.Class, UML.Property)
@group.register(UML.DataType, UML.Property)
@group.register(UML.Interface, UML.Property)
def property_group(
    parent: UML.Artifact | UML.Class | UML.DataType | UML.Interface,
    element: UML.Property,
) -> bool:
    if element.association:
        return False

    if element.owner:
        ungroup(element.owner, element)

    parent.ownedAttribute = element
    return True


@ungroup.register(UML.Artifact, UML.Property)
@ungroup.register(UML.Class, UML.Property)
@ungroup.register(UML.DataType, UML.Property)
@ungroup.register(UML.Interface, UML.Property)
def property_ungroup(
    parent: UML.Artifact | UML.Class | UML.DataType | UML.Interface,
    element: UML.Property,
) -> bool:
    if not element.association and element in parent.ownedAttribute:
        del parent.ownedAttribute[element]
        return True
    return False


@group.register(UML.Artifact, UML.Operation)
@group.register(UML.Class, UML.Operation)
@group.register(UML.DataType, UML.Operation)
@group.register(UML.Interface, UML.Operation)
def operation_group(
    parent: UML.Artifact | UML.Class | UML.DataType | UML.Interface,
    element: UML.Operation,
) -> bool:
    if element.owner:
        ungroup(element.owner, element)

    parent.ownedOperation = element
    return True


@ungroup.register(UML.Artifact, UML.Operation)
@ungroup.register(UML.Class, UML.Operation)
@ungroup.register(UML.DataType, UML.Operation)
@ungroup.register(UML.Interface, UML.Operation)
def operation_ungroup(
    parent: UML.Artifact | UML.Class | UML.DataType | UML.Interface,
    element: UML.Operation,
) -> bool:
    if element in parent.ownedOperation:
        del parent.ownedOperation[element]
        return True
    return False
