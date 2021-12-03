from gaphas.item import Item

from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.UML.actions.activitynodes import DecisionNodeItem, ForkNodeItem


def test_fork_node_item_implements_item_protocol(diagram):
    fork_node_item = diagram.create(ForkNodeItem)

    assert isinstance(fork_node_item, Item)


def test_decision_node_persistence(diagram, element_factory, saver, loader):
    item = diagram.create(
        DecisionNodeItem, subject=element_factory.create(UML.DecisionNode)
    )

    data = saver()
    loader(data)
    new_diagram = next(element_factory.select(Diagram))
    item = next(new_diagram.select(DecisionNodeItem))

    assert item.combined is None, item.combined


def test_combined_decision_node_persistence(diagram, element_factory, saver, loader):
    item = diagram.create(
        DecisionNodeItem, subject=element_factory.create(UML.DecisionNode)
    )
    merge_node = element_factory.create(UML.MergeNode)
    item.combined = merge_node

    data = saver()
    loader(data)
    new_diagram = next(element_factory.select(Diagram))
    item = next(new_diagram.select(DecisionNodeItem))

    assert item.combined is not None, item.combined
    assert isinstance(item.combined, UML.MergeNode)


def test_fork_node_persistence(diagram, element_factory, saver, loader):
    item = diagram.create(ForkNodeItem, subject=element_factory.create(UML.ForkNode))

    data = saver()
    loader(data)

    new_diagram = next(element_factory.select(Diagram))
    item = next(new_diagram.select(ForkNodeItem))
    assert item.combined is None, item.combined


def test_combined_fork_node_persistence(diagram, element_factory, saver, loader):
    item = diagram.create(ForkNodeItem, subject=element_factory.create(UML.ForkNode))

    merge_node = element_factory.create(UML.JoinNode)
    item.combined = merge_node

    data = saver()
    loader(data)
    new_diagram = next(element_factory.select(Diagram))
    item = next(new_diagram.select(ForkNodeItem))

    assert item.combined is not None, item.combined
    assert isinstance(item.combined, UML.JoinNode)
