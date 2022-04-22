from gaphor.diagram.drop import drop
from gaphor.diagram.presentation import connect
from gaphor.diagram.support import get_diagram_item
from gaphor.SysML.sysml import ProxyPort
from gaphor.UML.drop import diagram_has_presentation


@drop.register
def drop_proxy_port(element: ProxyPort, diagram, x, y):
    item_class = get_diagram_item(type(element))
    if not item_class:
        return None

    head_item = diagram_has_presentation(diagram, element.encapsulatedClassifier)
    if not head_item:
        return None

    item = diagram.create(item_class)
    assert item

    item.matrix.translate(x, y)
    item.subject = element

    connect(item, item.handles()[0], head_item)

    return item
