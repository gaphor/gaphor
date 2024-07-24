import pytest

from gaphor import UML
from gaphor.diagram.copypaste import copy_full, paste_link
from gaphor.diagram.group import group
from gaphor.diagram.tests.fixtures import copy_clear_and_paste_link
from gaphor.UML.deployments import ArtifactItem, NodeItem


@pytest.fixture
def node_with_artifact(diagram, element_factory):
    node = element_factory.create(UML.Node)
    artifact = element_factory.create(UML.Artifact)
    node_item = diagram.create(NodeItem, subject=node)
    artifact_item = diagram.create(ArtifactItem, subject=artifact)

    group(node_item, artifact_item)
    artifact_item.change_parent(node_item)

    assert artifact_item.parent is node_item

    return node_item, artifact_item


def test_copy_paste_of_nested_item(diagram, node_with_artifact):
    node_item, artifact_item = node_with_artifact

    buffer = copy_full({artifact_item})

    (new_comp_item,) = paste_link(buffer, diagram)

    assert new_comp_item.parent is node_item


def test_copy_paste_of_item_with_nested_item(diagram, node_with_artifact):
    buffer = copy_full(set(node_with_artifact))

    new_items = paste_link(buffer, diagram)

    new_node_item = next(i for i in new_items if isinstance(i, NodeItem))
    new_comp_item = next(i for i in new_items if isinstance(i, ArtifactItem))

    assert new_comp_item.parent is new_node_item


def test_copy_remove_paste_of_item_with_nested_item(
    diagram, element_factory, node_with_artifact
):
    new_items = copy_clear_and_paste_link(
        set(node_with_artifact), diagram, element_factory
    )

    new_node_item = next(i for i in new_items if isinstance(i, NodeItem))
    new_comp_item = next(i for i in new_items if isinstance(i, ArtifactItem))

    assert new_comp_item.parent is new_node_item
