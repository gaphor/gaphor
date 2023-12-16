from gaphor.diagram.drop import drop
from gaphor.diagram.presentation import connect
from gaphor.diagram.support import get_diagram_item
from gaphor.UML.uml import ActivityParameterNode


@drop.register
def drop_relationship(element: ActivityParameterNode, diagram, x, y):
    item_class = get_diagram_item(type(element))
    if not item_class:
        return None

    def drop_distance_to_item(item):
        local_x, local_y = item.matrix_i2c.inverse().transform_point(x, y)
        return item.point(local_x, local_y)

    appendable_item = min(
        diagram.select(
            lambda item: element.activity and element.activity is item.subject
        ),
        key=drop_distance_to_item,
        default=None,
    )

    if not appendable_item:
        return None

    item = diagram.create(item_class, subject=element)
    item.matrix.translate(x, y)
    item.change_parent(appendable_item)
    connect(item, item.handles()[0], appendable_item)

    return item
