from gaphor.C4Model import c4model
from gaphor.core.styling import FontWeight, TextAlign, VerticalAlign
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, EditableText, Text, draw_border
from gaphor.diagram.support import represents


@represents(c4model.C4Container)
class C4ContainerItem(ElementPresentation, Named):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("subject[NamedElement].name")
        self.watch("subject[C4Container].technology")
        self.watch("subject[C4Container].description")
        self.watch("subject[C4Container].type")

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                EditableText(
                    text=lambda: self.subject.name or "",
                    style={"font-weight": FontWeight.BOLD},
                ),
                Text(
                    text=lambda: self.subject.technology
                    and f"[component: {self.subject.technology}]"
                    or "[component]",
                    style={"font-size": "x-small"},
                ),
                Text(
                    text=lambda: self.subject.description or "",
                ),
                style={"padding": (4, 4, 4, 4)},
            ),
            style={
                "text-align": TextAlign.LEFT
                if self.diagram and self.children
                else TextAlign.CENTER,
                "vertical-align": VerticalAlign.BOTTOM
                if self.diagram and self.children
                else VerticalAlign.MIDDLE,
            },
            draw=draw_border,
        )
