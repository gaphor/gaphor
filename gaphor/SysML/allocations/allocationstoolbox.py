from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection, new_item_factory
from gaphor.SysML.allocations.relationships import AllocateItem

allocations = ToolSection(
    gettext("Allocations"),
    (
        ToolDef(
            "toolbox-allocate-dependency",
            gettext("Allocate"),
            "gaphor-allocate-symbolic",
            None,
            new_item_factory(AllocateItem),
        ),
    ),
)
