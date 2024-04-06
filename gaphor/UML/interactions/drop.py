from gaphor.core.modeling import Diagram
from gaphor.diagram.drop import drop, drop_element
from gaphor.UML.interactions.lifeline import LifelineItem
from gaphor.UML.uml import ConnectableElement


@drop.register(ConnectableElement, Diagram)
def drop_connectable_element(element: ConnectableElement, diagram, x, y):
    def drop_distance_to_item(item):
        local_x, local_y = item.matrix_i2c.inverse().transform_point(x, y)
        return item.point(local_x, local_y)

    lifeline_item: LifelineItem | None = next(
        (
            item
            for item in diagram.select(LifelineItem)
            if drop_distance_to_item(item) <= 0.0
        ),
        None,
    )

    if lifeline_item and lifeline_item.subject:
        lifeline_item.subject.represents = element
        return lifeline_item

    return drop_element(element, diagram, x, y)
