import pytest

from gaphor import UML
from gaphor.diagram.diagramtools import PlacementTool
from gaphor.UML.actions.actionstoolbox import partition_config
from gaphor.UML.actions.partition import PartitionItem


@pytest.fixture
def partition_item_factory():
    return PlacementTool.new_item_factory(
        PartitionItem,
        UML.ActivityPartition,
        config_func=partition_config,
    )


@pytest.fixture
def new_partition(partition_item_factory, diagram):
    return partition_item_factory(diagram)


def test_partition_placement_adds_two_partitions(new_partition: PartitionItem):

    assert new_partition.subject in new_partition.partition
    assert len(new_partition.partition) == 2
