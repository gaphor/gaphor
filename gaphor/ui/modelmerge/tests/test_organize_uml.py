from typing import Iterable

from gaphor import UML
from gaphor.core.changeset.compare import compare
from gaphor.core.modeling import (
    ElementFactory,
    PendingChange,
)
from gaphor.diagram.tests.fixtures import connect
from gaphor.SysML import sysml
from gaphor.SysML.diagramitems import BlockItem, PropertyItem, ProxyPortItem
from gaphor.SysML.propertypages import create_item_flow
from gaphor.ui.modelmerge.organize import Node, organize_changes
from gaphor.UML.actions.actionstoolbox import partition_config
from gaphor.UML.diagramitems import (
    ActivityItem,
    AssociationItem,
    ClassItem,
    ConnectorItem,
    ExtensionItem,
    PartitionItem,
    StateItem,
    TransitionItem,
)
from gaphor.UML.recipes import apply_stereotype
from gaphor.UML.umllex import parse


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
    all(compare(current, current, element_factory))
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
    all(compare(current, current, element_factory))
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
    all(compare(current, current, element_factory))
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
    all(compare(current, current, element_factory))
    tree = list(organize_changes(current, modeling_language))

    assert len(tree) == 1
    assert {e.id for e in current.select(PendingChange)} == set(all_change_ids(tree))


def test_activity_with_parameter_node(element_factory, modeling_language, create):
    activity = create(ActivityItem, UML.Activity)
    node = element_factory.create(UML.ActivityParameterNode)
    node.parameter = element_factory.create(UML.Parameter)
    activity.subject.node = node

    current = ElementFactory()
    all(compare(current, current, element_factory))
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
    all(compare(current, current, element_factory))
    tree = list(organize_changes(current, modeling_language))

    # Create diagram + extra Activity
    assert len(tree) == 2
    assert {e.id for e in current.select(PendingChange)} == set(all_change_ids(tree))


def test_connector_with_item_flow(element_factory, modeling_language, create):
    block_item = create(BlockItem, sysml.Block)
    property_item = create(PropertyItem, UML.Property)
    proxy_port_item = create(ProxyPortItem)
    connector_item = create(ConnectorItem)
    connect(proxy_port_item, proxy_port_item.handles()[0], block_item)
    connect(connector_item, connector_item.head, proxy_port_item)
    connect(connector_item, connector_item.tail, property_item)
    create_item_flow(connector_item.subject)

    current = ElementFactory()
    all(compare(current, current, element_factory))
    tree = list(organize_changes(current, modeling_language))

    assert len(tree) == 3
    assert {e.id for e in current.select(PendingChange)} == set(all_change_ids(tree))


def test_state_with_entry_do_exit_criteria(element_factory, modeling_language, create):
    state_item = create(StateItem, UML.State)
    state_item.subject.entry = element_factory.create(UML.Activity)
    state_item.subject.doActivity = element_factory.create(UML.Activity)

    current = ElementFactory()
    all(compare(current, current, element_factory))
    tree = list(organize_changes(current, modeling_language))

    assert len(tree) == 1
    assert {e.id for e in current.select(PendingChange)} == set(all_change_ids(tree))


def test_transition_with_guard(element_factory, modeling_language, create):
    head_state_item = create(StateItem, UML.State)
    tail_state_item = create(StateItem, UML.State)
    transition_item = create(TransitionItem)
    connect(transition_item, transition_item.head, head_state_item)
    connect(transition_item, transition_item.tail, tail_state_item)

    current = ElementFactory()
    all(compare(current, current, element_factory))
    tree = list(organize_changes(current, modeling_language))

    assert transition_item.subject.guard
    assert len(tree) == 1
    assert {e.id for e in current.select(PendingChange)} == set(all_change_ids(tree))


def test_applied_stereotype(element_factory, modeling_language, create):
    stereotype = element_factory.create(UML.Stereotype)
    class_item = create(ClassItem, UML.Class)
    apply_stereotype(class_item.subject, stereotype)

    current = ElementFactory()
    all(compare(current, current, element_factory))
    tree = list(organize_changes(current, modeling_language))

    # Create Stereotype + create diagram
    assert len(tree) == 2
    assert {e.id for e in current.select(PendingChange)} == set(all_change_ids(tree))
