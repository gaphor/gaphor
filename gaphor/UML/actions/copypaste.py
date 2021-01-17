from gaphor.diagram.copypaste import copy, copy_presentation
from gaphor.UML.actions.partition import PartitionItem


@copy.register
def copy_class(element: PartitionItem):
    yield element.id, copy_presentation(element)
    for partition in element.partition:
        yield from copy(partition)
