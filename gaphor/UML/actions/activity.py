from gaphor import UML
from gaphor.diagram.presentation import Classified, ElementPresentation
from gaphor.diagram.shapes import Box, Text, TextAlign, VerticalAlign, draw_border
from gaphor.diagram.support import represents
from gaphor.UML.recipes import stereotypes_str


@represents(UML.Activity)
class ActivityItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=50, height=30)

        self.width = 100
        self.shape = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
                style={"text-align": TextAlign.LEFT},
            ),
            Text(
                text=lambda: self.subject.name or "",
                style={"text-align": TextAlign.LEFT},
            ),
            style={
                "padding": (4, 12, 4, 12),
                "border-radius": 20,
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_border,
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch(
            "subject[Activity].node[ActivityParameterNode].parameter.name",
            self.on_parameter_update,
        )
        self.watch(
            "subject[Activity].node[ActivityParameterNode].parameter.typeValue",
            self.on_parameter_update,
        )

    def postload(self):
        super().postload()
        self.on_parameter_update()

    def on_parameter_update(self, event=None):
        diagram = self.diagram
        parameter_nodes = [
            p for p in self.subject.node if isinstance(p, UML.ActivityParameterNode)
        ]
        parameter_items = {
            i.subject: i
            for i in self.children
            if isinstance(i, ActivityParameterNodeItem)
        }

        for node in parameter_nodes:
            if node not in parameter_items:
                diagram.create(ActivityParameterNodeItem, parent=self, subject=node)

        for node in parameter_items:
            if node not in parameter_nodes:
                del self.children[parameter_items[node]]


class ActivityParameterNodeItem(ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=50, height=30)

        self.width = 100
        self.shape = Box(
            Text(
                text=lambda: self.subject.parameter.name or "",
            ),
            style={"padding": (4, 12, 4, 12), "background-color": (1, 1, 1, 1)},
            draw=draw_border,
        )
        self.watch("subject[ActivityParameterNode].parameter.name")
