from gaphor.C4Model import c4model
from gaphor.core import gettext
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
        self.watch("children", self.update_shapes)

    def update_shapes(self, event=None):
        text_align = (
            TextAlign.LEFT if self.diagram and self.children else TextAlign.CENTER
        )
        self.shape = Box(
            EditableText(
                text=lambda: self.subject.name or "",
                style={"font-weight": FontWeight.BOLD, "text-align": text_align},
            ),
            Text(
                text=lambda: self.subject.technology
                and f"[{gettext(self.subject.type)}: {self.subject.technology}]"
                or f"[{gettext(self.subject.type)}]",
                style={"font-size": "x-small", "text-align": text_align},
            ),
            Text(
                text=lambda: self.subject.description or "",
                style={"text-align": text_align},
            ),
            style={
                "padding": (4, 4, 4, 4),
                "vertical-align": VerticalAlign.BOTTOM
                if self.diagram and self.children
                else VerticalAlign.MIDDLE,
            },
            draw=draw_border,
        )
