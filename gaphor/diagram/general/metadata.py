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


class MetadataItem(ElementPresentation):
    createdBy: attribute[str] = attribute("createdBy", str, "")
    description: attribute[str] = attribute("description", str, "")
    website: attribute[str] = attribute("website", str, "")
    revision: attribute[str] = attribute("revision", str, "")
    license: attribute[str] = attribute("license", str, "")
    createdOn: attribute[str] = attribute("createdOn", str, "")
    updatedOn: attribute[str] = attribute("updatedOn", str, "")

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("createdBy", self.update_shapes).watch(
            "website", self.update_shapes
        ).watch("description", self.update_shapes).watch(
            "revision", self.update_shapes
        ).watch(
            "license", self.update_shapes
        ).watch(
            "createdOn", self.update_shapes
        ).watch(
            "updatedOn", self.update_shapes
        )

    def update_shapes(self, event=None):
        diagram = self.diagram
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
            *(
                [
                    Box(
                        *(
                            [
                                Box(
                                    Text(
                                        text=f'{diagram.gettext("Created By")}:',
                                        style=heading_style,
                                    ),
                                    Text(
                                        text=lambda: self.createdBy or "",
                                        style=text_style,
                                    ),
                                    style=box_style,
                                )
                            ]
                            if self.createdBy
                            else []
                        ),
                        *(
                            [
                                Box(
                                    Text(
                                        text=f'{diagram.gettext("Website")}:',
                                        style=heading_style,
                                    ),
                                    Text(
                                        text=lambda: self.website or "",
                                        style=text_style,
                                    ),
                                    style=box_style,
                                    draw=draw_left_separator,
                                )
                            ]
                            if self.website
                            else []
                        ),
                        orientation=Orientation.HORIZONTAL,
                        style=group_style,
                    )
                ]
                if self.createdBy or self.website
                else []
            ),
            *(
                [
                    Box(
                        Text(
                            text=f'{diagram.gettext("Description")}:',
                            style=heading_style,
                        ),
                        Text(
                            text=lambda: self.description or "",
                            style=text_style,
                        ),
                        style=box_style,
                        draw=draw_top_separator,
                    )
                ]
                if self.description
                else []
            ),
            *(
                [
                    Box(
                        *(
                            [
                                Box(
                                    Text(
                                        text=f'{diagram.gettext("Revision")}:',
                                        style=heading_style,
                                    ),
                                    Text(
                                        text=lambda: self.revision or "",
                                        style=text_style,
                                    ),
                                    style=box_style,
                                )
                            ]
                            if self.revision
                            else []
                        ),
                        *(
                            [
                                Box(
                                    Text(
                                        text=f'{diagram.gettext("License")}:',
                                        style=heading_style,
                                    ),
                                    Text(
                                        text=lambda: self.license or "",
                                        style=text_style,
                                    ),
                                    style=box_style,
                                    draw=draw_left_separator,
                                )
                            ]
                            if self.license
                            else []
                        ),
                        *(
                            [
                                Box(
                                    Text(
                                        text=f'{diagram.gettext("Created On")}:',
                                        style=heading_style,
                                    ),
                                    Text(
                                        text=lambda: self.createdOn or "",
                                        style=text_style,
                                    ),
                                    style=box_style,
                                    draw=draw_left_separator,
                                )
                            ]
                            if self.createdOn
                            else []
                        ),
                        *(
                            [
                                Box(
                                    Text(
                                        text=f'{diagram.gettext("Updated On")}:',
                                        style=heading_style,
                                    ),
                                    Text(
                                        text=lambda: self.updatedOn or "",
                                        style=text_style,
                                    ),
                                    style=box_style,
                                    draw=draw_left_separator,
                                )
                            ]
                            if self.updatedOn
                            else []
                        ),
                        orientation=Orientation.HORIZONTAL,
                        style=group_style,
                        draw=draw_top_separator,
                    )
                ]
                if self.revision or self.license or self.createdOn or self.updatedOn
                else []
            ),
            draw=draw_border,
            style=group_style,
        )
