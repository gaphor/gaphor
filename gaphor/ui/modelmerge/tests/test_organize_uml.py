from typing import Iterable

from gaphor.core.modeling import (
    ElementFactory,
    PendingChange,
)
from gaphor import UML
from gaphor.UML.diagramitems import (
    ClassItem,
    AssociationItem,
    ExtensionItem,
    ActivityItem,
    PartitionItem,
)
from gaphor.ui.modelmerge.organize import organize_changes, Node
from gaphor.UML.umllex import parse
from gaphor.core.changeset.compare import compare
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML.actions.actionstoolbox import partition_config


def all_change_ids(nodes: Iterable[Node]):
    for n in nodes:
        yield from (e.id for e in n.elements)
        if n.children:
            yield from all_change_ids(n.children)


def test_class_with_members(element_factory, modeling_language, create):
    class_item = create(ClassItem, UML.Class)
    class_item.subject.name = "MyClass"
    class_item.subject.ownedAttribute = element_factory.create(UML.Property)
    parse(class_item.subject.ownedAttribute[0], "+foo: int")
    class_item.subject.ownedOperation = element_factory.create(UML.Operation)
    parse(class_item.subject.ownedOperation[0], "+ to_string(arg: int): str")

    current = ElementFactory()
    all(compare(current, element_factory))
    tree = list(organize_changes(current, modeling_language))

    assert len(tree) == 1
    assert {e.id for e in current.select(PendingChange)} == set(all_change_ids(tree))


def test_association(element_factory, modeling_language, create):
    head_class_item = create(ClassItem, UML.Class)
    tail_class_item = create(ClassItem, UML.Class)
    association = create(AssociationItem)
    connect(association, association.head, head_class_item)
    connect(association, association.tail, tail_class_item)

    current = ElementFactory()
    all(compare(current, element_factory))
    tree = list(organize_changes(current, modeling_language))

    assert len(tree) == 1
    assert {e.id for e in current.select(PendingChange)} == set(all_change_ids(tree))


def test_association_with_existing_classes(element_factory, modeling_language, create):
    head_class_item = create(ClassItem, UML.Class)
    tail_class_item = create(ClassItem, UML.Class)
    association = create(AssociationItem)
    connect(association, association.head, head_class_item)
    connect(association, association.tail, tail_class_item)

    current = ElementFactory()
    current.create_as(UML.Class, head_class_item.subject.id)
    current.create_as(UML.Class, tail_class_item.subject.id)
    all(compare(current, element_factory))
    tree = list(organize_changes(current, modeling_language))

    assert len(tree) == 3
    assert {e.id for e in current.select(PendingChange)} == set(all_change_ids(tree))


def test_extension(element_factory, modeling_language, create):
    class_item = create(ClassItem, UML.Class)
    stereotype_item = create(ClassItem, UML.Stereotype)
    extension = create(ExtensionItem)
    connect(extension, extension.head, class_item)
    connect(extension, extension.tail, stereotype_item)

    current = ElementFactory()
    all(compare(current, element_factory))
    tree = list(organize_changes(current, modeling_language))

    assert len(tree) == 1
    assert {e.id for e in current.select(PendingChange)} == set(all_change_ids(tree))


def test_activity_with_parameter_node(element_factory, modeling_language, create):
    activity = create(ActivityItem, UML.Activity)
    node = element_factory.create(UML.ActivityParameterNode)
    node.parameter = element_factory.create(UML.Parameter)
    activity.subject.node = node

    current = ElementFactory()
    all(compare(current, element_factory))
    tree = list(organize_changes(current, modeling_language))

    assert len(tree) == 1
    assert {e.id for e in current.select(PendingChange)} == set(all_change_ids(tree))


def test_partition_with_swim_lanes(element_factory, modeling_language, create):
    partition = create(PartitionItem, UML.ActivityPartition)
    # NB. This adds an extra Activity namespace!
    partition_config(partition)

    partition.partition = element_factory.create(UML.ActivityPartition)
    partition.partition = element_factory.create(UML.ActivityPartition)
    partition.partition[0].activity = partition.subject.activity
    partition.partition[1].activity = partition.subject.activity

    current = ElementFactory()
    all(compare(current, element_factory))
    tree = list(organize_changes(current, modeling_language))

    # Create diagram + extra Activity
    assert len(tree) == 2
    assert {e.id for e in current.select(PendingChange)} == set(all_change_ids(tree))
