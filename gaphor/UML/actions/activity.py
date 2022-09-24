from gaphor import UML
from gaphor.diagram.presentation import (
    AttachedPresentation,
    Classified,
    ElementPresentation,
    connect,
)
from gaphor.diagram.shapes import Box, JustifyContent, Text, TextAlign, draw_border
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontStyle
from gaphor.UML.recipes import stereotypes_str


@represents(UML.Activity)
class ActivityItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=50, height=50)

        self.width = 100

        self.watch("subject[NamedElement].name").watch(
            "subject.appliedStereotype.classifier.name"
        ).watch("subject[Classifier].isAbstract", self.update_shapes).watch(
            "subject[Activity].node[ActivityParameterNode].parameter.name",
            self.update_parameters,
        ).watch(
            "subject[Activity].node[ActivityParameterNode].parameter.typeValue",
            self.update_parameters,
        )

    def postload(self):
        super().postload()
        self.update_parameters()

    def update_shapes(self, event=None):
        self.shape = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
                style={"text-align": TextAlign.LEFT},
            ),
            Text(
                text=lambda: self.subject.name or "",
                style={
                    "text-align": TextAlign.LEFT,
                    "font-style": FontStyle.ITALIC
                    if self.subject and self.subject.isAbstract
                    else FontStyle.NORMAL,
                },
            ),
            style={
                "padding": (4, 12, 4, 12),
                "border-radius": 20,
                "justify-content": JustifyContent.START,
            },
            draw=draw_border,
        )

    def update_parameters(self, event=None):
        diagram = self.diagram
        parameter_nodes = (
            [p for p in self.subject.node if isinstance(p, UML.ActivityParameterNode)]
            if self.subject
            else []
        )
        parameter_items = {
            i.subject: i
            for i in self.children
            if isinstance(i, ActivityParameterNodeItem)
        }

        for node in parameter_nodes:
            if node not in parameter_items:
                item = diagram.create(
                    ActivityParameterNodeItem, parent=self, subject=node
                )
                item.matrix.translate(0, 10)
                connect(item, item.handles()[0], self)

        for node in parameter_items:
            if node not in parameter_nodes:
                del self.children[parameter_items[node]]


class ActivityParameterNodeItem(AttachedPresentation[UML.ActivityParameterNode]):
    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape=Box(
                Text(
                    text=lambda: self.subject.parameter.name or "",
                ),
                style={"padding": (4, 12, 4, 12), "background-color": (1, 1, 1, 1)},
                draw=draw_border,
            ),
            width=100,
            height=30,
        )

        self.watch("subject[ActivityParameterNode].parameter.name")
