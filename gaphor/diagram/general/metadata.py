from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import (
    Style,
    TextAlign,
    VerticalAlign,
    FontWeight,
    JustifyContent,
)
from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.shapes import (
    Box,
    Text,
    draw_border,
    draw_left_separator,
    draw_top_separator,
    Orientation,
)
from gaphor.i18n import gettext


class MetadataItem(ElementPresentation):
    createdBy: attribute[str] = attribute("createdBy", str, "")
    website: attribute[str] = attribute("website", str, "")
    description: attribute[str] = attribute("description", str, "")
    revision: attribute[str] = attribute("revision", str, "")
    license: attribute[str] = attribute("license", str, "")
    createdAt: attribute[str] = attribute("createdAt", str, "")
    updatedAt: attribute[str] = attribute("updatedAt", str, "")

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        # Some test data:
        self.createdBy = "Alice A. Gaphor"
        self.website = "https://gaphor.org"
        self.description = "Prototype model SX-1"
        self.revision = "0.1A"
        self.license = "CC-PDDC"
        self.createdAt = "2021-06-11"
        self.updatedAt = "2021-12-06"

        group_style: Style = {"justify-content": JustifyContent.STRETCH}
        box_style: Style = {"padding": (4, 4, 4, 4)}
        text_style: Style = {
            "text-align": TextAlign.LEFT,
            "vertical-align": VerticalAlign.TOP,
        }
        heading_style: Style = {
            **text_style,  # type: ignore[misc]
            "font-size": "small",
            "font-weight": FontWeight.BOLD,
        }

        self.shape = Box(
            Box(
                Box(
                    Text(
                        text=gettext("created by:"),
                        style=heading_style,
                    ),
                    Text(
                        text=lambda: self.createdBy or "",
                        style=text_style,
                    ),
                    style=box_style,
                ),
                Box(
                    Text(
                        text=gettext("website:"),
                        style=heading_style,
                    ),
                    Text(
                        text=lambda: self.website or "",
                        style=text_style,
                    ),
                    style=box_style,
                    draw=draw_left_separator,
                ),
                orientation=Orientation.HORIZONTAL,
                style=group_style,
            ),
            Box(
                Text(
                    text=gettext("description:"),
                    style=heading_style,
                ),
                Text(
                    text=lambda: self.description or "",
                    style=text_style,
                ),
                style=box_style,
                draw=draw_top_separator,
            ),
            Box(
                Box(
                    Text(
                        text=gettext("revision:"),
                        style=heading_style,
                    ),
                    Text(
                        text=lambda: self.revision or "",
                        style=text_style,
                    ),
                    style=box_style,
                ),
                Box(
                    Text(
                        text=gettext("license:"),
                        style=heading_style,
                    ),
                    Text(
                        text=lambda: self.license or "",
                        style=text_style,
                    ),
                    style=box_style,
                    draw=draw_left_separator,
                ),
                Box(
                    Text(
                        text=gettext("created at:"),
                        style=heading_style,
                    ),
                    Text(
                        text=lambda: self.createdAt or "",
                        style=text_style,
                    ),
                    style=box_style,
                    draw=draw_left_separator,
                ),
                Box(
                    Text(
                        text=gettext("updated at:"),
                        style=heading_style,
                    ),
                    Text(
                        text=lambda: self.updatedAt or "",
                        style=text_style,
                    ),
                    style=box_style,
                    draw=draw_left_separator,
                ),
                orientation=Orientation.HORIZONTAL,
                style=group_style,
                draw=draw_top_separator,
            ),
            draw=draw_border,
            style=group_style,
        )
        self.watch("description")
