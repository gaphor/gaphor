from gaphor.C4Model import c4model
from gaphor.core.styling import FontStyle, FontWeight, TextAlign, VerticalAlign
from gaphor.diagram.presentation import Classified, ElementPresentation
from gaphor.diagram.shapes import Box, EditableText, Text, draw_border
from gaphor.diagram.support import represents


@represents(c4model.C4Container)
class C4ContainerItem(ElementPresentation, Classified):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("subject[NamedElement].name")
        self.watch("subject[C4Extension].technology")
        self.watch("subject[C4Extension].description")
        self.watch("subject[Classifier].isAbstract", self.update_shapes)

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                EditableText(
                    text=lambda: self.subject.name or "",
                    style={
                        "font-weight": FontWeight.BOLD,
                        "font-style": self.subject.isAbstract
                        and FontStyle.ITALIC
                        or FontStyle.NORMAL,
                    },
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
