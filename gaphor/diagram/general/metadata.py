from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.shapes import (
    Box,
    CssNode,
    Orientation,
    Text,
    draw_border,
    draw_left_separator,
    draw_top_separator,
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
        ).watch("license", self.update_shapes).watch(
            "createdOn", self.update_shapes
        ).watch("updatedOn", self.update_shapes)

    def update_shapes(self, event=None):
        diagram = self.diagram
        self.shape = Box(
            *(
                [
                    Box(
                        *(
                            [
                                cell(
                                    heading(f'{diagram.gettext("Created By")}:'),
                                    content(lambda: self.createdBy or ""),
                                )
                            ]
                            if self.createdBy
                            else []
                        ),
                        *(
                            [
                                cell(
                                    heading(f'{diagram.gettext("Website")}:'),
                                    content(lambda: self.website or ""),
                                    draw=draw_left_separator,
                                )
                            ]
                            if self.website
                            else []
                        ),
                        orientation=Orientation.HORIZONTAL,
                    )
                ]
                if self.createdBy or self.website
                else []
            ),
            *(
                [
                    cell(
                        heading(f'{diagram.gettext("Description")}:'),
                        content(lambda: self.description or ""),
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
                                cell(
                                    heading(f'{diagram.gettext("Revision")}:'),
                                    content(lambda: self.revision or ""),
                                )
                            ]
                            if self.revision
                            else []
                        ),
                        *(
                            [
                                cell(
                                    heading(f'{diagram.gettext("License")}:'),
                                    content(lambda: self.license or ""),
                                    draw=draw_left_separator,
                                )
                            ]
                            if self.license
                            else []
                        ),
                        *(
                            [
                                cell(
                                    heading(f'{diagram.gettext("Created On")}:'),
                                    content(lambda: self.createdOn or ""),
                                    draw=draw_left_separator,
                                )
                            ]
                            if self.createdOn
                            else []
                        ),
                        *(
                            [
                                cell(
                                    heading(f'{diagram.gettext("Updated On")}:'),
                                    content(lambda: self.updatedOn or ""),
                                    draw=draw_left_separator,
                                )
                            ]
                            if self.updatedOn
                            else []
                        ),
                        orientation=Orientation.HORIZONTAL,
                        draw=draw_top_separator,
                    )
                ]
                if self.revision or self.license or self.createdOn or self.updatedOn
                else []
            ),
            draw=draw_border,
        )


def cell(*children, draw=None):
    return CssNode("cell", None, Box(*children, draw=draw))


def heading(text):
    return CssNode("heading", None, Text(text=text))


def content(text):
    return CssNode("content", None, Text(text=text))
