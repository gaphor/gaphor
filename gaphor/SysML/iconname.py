from gaphor.diagram.iconname import icon_name
from gaphor.SysML.sysml import SysMLDiagram


@icon_name.register(SysMLDiagram)
def get_name_for_class(element):
    return "gaphor-diagram-symbolic"
