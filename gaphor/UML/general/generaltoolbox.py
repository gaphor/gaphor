import getpass
import time

from gaphas.item import SE

from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection, new_item_factory
from gaphor.diagram.general import diagramitems as general
from gaphor.UML import Comment, Image
from gaphor.UML.general import CommentItem, CommentLineItem, ImageItem


def metadata_config(metadata_item: general.MetadataItem) -> None:
    metadata_item.createdBy = getpass.getuser()
    metadata_item.description = metadata_item.diagram.name
    metadata_item.revision = "1.0"
    metadata_item.createdOn = time.strftime("%Y-%m-%d")


def image_config(image_item: ImageItem) -> None:
    image_item.subject.name = gettext("New Image")


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
            "toolbox-ellipse",
            gettext("Ellipse"),
            "gaphor-ellipse-symbolic",
            "e",
            new_item_factory(general.Ellipse),
            SE,
        ),
        ToolDef(
            "toolbox-comment",
            gettext("Comment"),
            "gaphor-comment-symbolic",
            "k",
            new_item_factory(CommentItem, Comment),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-comment-line",
            gettext("Comment line"),
            "gaphor-comment-line-symbolic",
            "<Shift>K",
            new_item_factory(CommentLineItem),
        ),
        ToolDef(
            "toolbox-metadata",
            gettext("Diagram metadata"),
            "gaphor-metadata-symbolic",
            None,
            new_item_factory(general.MetadataItem, config_func=metadata_config),
        ),
        ToolDef(
            "toolbox-image",
            gettext("Picture"),
            "gaphor-picture-symbolic",
            None,
            new_item_factory(ImageItem, Image, config_func=image_config),
            handle_index=SE,
        ),
    ),
)
