from gaphor.diagram.deletable import deletable
from gaphor.SysML.diagramframe import DiagramFrameItem


@deletable.register
def deletable_diagram_frame_item(item: DiagramFrameItem):
    return False
