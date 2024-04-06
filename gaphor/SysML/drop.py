from gaphor.core.modeling import Diagram
from gaphor.diagram.drop import drop
from gaphor.diagram.presentation import connect
from gaphor.diagram.support import get_diagram_item
from gaphor.SysML.sysml import Block, ProxyPort
from gaphor.UML.uml import Property


@drop.register(ProxyPort, Diagram)
def drop_proxy_port(element: ProxyPort, diagram: Diagram, x, y):
    item_class = get_diagram_item(type(element))
    if not item_class:
        return None

    def port_owning_item_block(item):
        match item.subject:
            case Property():
                block = (
                    item.subject.type if isinstance(item.subject.type, Block) else None
                )
            case Block():
                block = item.subject
            case _:
                return False
        return element in block.ownedPort if block else False

    def drop_distance_to_item(item):
        local_x, local_y = item.matrix_i2c.inverse().transform_point(x, y)
        return item.point(local_x, local_y)

    head_item = min(
        diagram.select(lambda item: port_owning_item_block(item)),
        key=drop_distance_to_item,
        default=None,
    )

    if not head_item:
        return None

    item = diagram.create(item_class)
    assert item

    item.matrix.translate(x, y)
    item.subject = element

    connect(item, item.handles()[0], head_item)

    return item
