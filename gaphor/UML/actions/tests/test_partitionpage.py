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
    num_partitions.set_value(4)

    assert len(item.partition) == 4


def test_partition_name(diagram, element_factory):
    item = diagram.create(
        UML.actions.PartitionItem, subject=element_factory.create(UML.ActivityPartition)
    )
    property_page = PartitionPropertyPage(item)
    property_page.construct()
    property_page.update_partitions(1)

    widget = property_page.construct_partition(item.partition[0])

    name = find(widget, "partition-name")
    name.set_text("Name")

    assert item.partition[0].name == "Name"


def test_partition_type(diagram, element_factory):
    class_ = element_factory.create(UML.Class)
    class_.name = "Foobar"
    item = diagram.create(
        UML.actions.PartitionItem, subject=element_factory.create(UML.ActivityPartition)
    )
    property_page = PartitionPropertyPage(item)
    property_page.construct()
    property_page.update_partitions(1)

    widget = property_page.construct_partition(item.partition[0])

    dropdown = find(widget, "partition-type")
    class_index = next(
        n for n, lv in enumerate(dropdown.get_model()) if lv.value == class_.id
    )
    dropdown.set_selected(class_index)

    assert item.partition[0].represents is class_
