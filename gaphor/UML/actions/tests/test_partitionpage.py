from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.actions.partitionpage import PartitionPropertyPage


def test_partition_page(diagram, element_factory):
    item = diagram.create(
        UML.actions.PartitionItem, subject=element_factory.create(UML.ActivityPartition)
    )
    property_page = PartitionPropertyPage(item)

    widget = property_page.construct()

    num_partitions = find(widget, "num-partitions")
    num_partitions.set_value(2)

    assert len(item.partition) == 2
