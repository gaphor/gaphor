import getpass
import time

from gaphas.item import SE

from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import (
    ToolboxDefinition,
    ToolDef,
    ToolSection,
    new_item_factory,
)
from gaphor.diagram.general import diagramitems as general
from gaphor.SysML2 import sysml2


def metadata_config(metadata_item: general.MetadataItem) -> None:
    metadata_item.createdBy = getpass.getuser()
    metadata_item.description = metadata_item.diagram.name
    metadata_item.revision = "1.0"
    metadata_item.createdOn = time.strftime("%Y-%m-%d")


def part_definition_config(box_item: general.Box) -> None:
    if (subject := box_item.subject) and hasattr(subject, "declaredName"):
        subject.declaredName = subject.declaredName or gettext("Part Definition")


def requirement_definition_config(box_item: general.Box) -> None:
    if (subject := box_item.subject) and hasattr(subject, "declaredName"):
        subject.declaredName = subject.declaredName or gettext("Requirement Definition")


general_tools = ToolSection(
    gettext("General"),
    (
        ToolDef(
            "toolbox-pointer",
            gettext("Pointer"),
            "gaphor-pointer-symbolic",
            "Escape",
            item_factory=None,
        ),
        ToolDef(
            "toolbox-magnet",
            gettext("Magnet"),
            "gaphor-magnet-symbolic",
            "F1",
            item_factory=None,
        ),
        ToolDef(
            "toolbox-line",
            gettext("Line"),
            "gaphor-line-symbolic",
            "l",
            new_item_factory(general.Line),
        ),
        ToolDef(
            "toolbox-box",
            gettext("Box"),
            "gaphor-box-symbolic",
            "b",
            new_item_factory(general.Box),
            SE,
        ),
        ToolDef(
            "toolbox-diamond",
            gettext("Diamond"),
            "gaphor-diamond-symbolic",
            None,
            new_item_factory(general.Diamond),
            SE,
        ),
        ToolDef(
            "toolbox-ellipse",
            gettext("Ellipse"),
            "gaphor-ellipse-symbolic",
            "e",
            new_item_factory(general.Ellipse),
            SE,
        ),
        ToolDef(
            "toolbox-metadata",
            gettext("Diagram metadata"),
            "gaphor-metadata-symbolic",
            None,
            new_item_factory(general.MetadataItem, config_func=metadata_config),
        ),
    ),
)

sysml2_tools = ToolSection(
    gettext("SysML 2"),
    (
        ToolDef(
            "toolbox-sysml2-part-definition",
            gettext("Part Definition"),
            "gaphor-box-symbolic",
            "p",
            new_item_factory(
                general.Box,
                sysml2.PartDefinition,
                config_func=part_definition_config,
            ),
            SE,
        ),
        ToolDef(
            "toolbox-sysml2-requirement-definition",
            gettext("Requirement Definition"),
            "gaphor-box-symbolic",
            "r",
            new_item_factory(
                general.Box,
                sysml2.RequirementDefinition,
                config_func=requirement_definition_config,
            ),
            SE,
        ),
    ),
)

sysml2_toolbox_actions: ToolboxDefinition = (
    general_tools,
    sysml2_tools,
)
