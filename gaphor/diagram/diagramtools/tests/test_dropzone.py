from gaphor import UML
from gaphor.diagram.diagramtools.dropzone import drop_zone_tool, on_motion
from gaphor.UML.components import ComponentItem, NodeItem


def test_hover_over_drop_zone(diagram, element_factory, view):
    node_item = diagram.create(NodeItem, subject=element_factory.create(UML.Node))
    node_item.width = node_item.height = 200
    comp_item = diagram.create(
        ComponentItem, subject=element_factory.create(UML.Component)
    )

    view.request_update((node_item, comp_item))

    tool = drop_zone_tool(view, ComponentItem)
    on_motion(tool, 100, 100, ComponentItem)

    selection = view.selection
    assert selection.dropzone_item is node_item
