from gaphor.diagram.drop import drop
from gaphor.diagram.presentation import connect
from gaphor.diagram.support import get_diagram_item
from gaphor.SysML.sysml import ProxyPort
from gaphor.UML.drop import diagram_has_presentation
from gaphor.SysML.blocks.property import PropertyItem
from gaphor.SysML.sysml import Block


@drop.register
def drop_proxy_port(element: ProxyPort, diagram, x, y):
    item_class = get_diagram_item(type(element))
    if not item_class:
        return None

    def property_item_which_is_typed_by_block_owning_the_port(item):
        return (
            isinstance(item, PropertyItem)
            and isinstance(item.subject.type, Block)
            and element in item.subject.type.ownedPort
        )

    head_item = next(
        iter(
            diagram.select(
                property_item_which_is_typed_by_block_owning_the_port
            )
        ),
        diagram_has_presentation(diagram, element.encapsulatedClassifier),
    )

    if not head_item:
        return None

    item = diagram.create(item_class)
    assert item

    item.matrix.translate(x, y)
    item.subject = element

    connect(item, item.handles()[0], head_item)

    return item
